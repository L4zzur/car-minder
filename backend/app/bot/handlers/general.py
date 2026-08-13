from datetime import UTC, datetime
from uuid import UUID

from aiogram import F, Router, html
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    Message,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.schemas import MileageLogCreate, ServiceItemMarkServiced
from repositories import (
    CarRepository,
    MileageLogRepository,
    ReminderRepository,
    ServiceItemRepository,
    UserRepository,
)
from services.exceptions import (
    TelegramAlreadyLinkedError,
    TelegramAlreadyLinkedToAnotherError,
)
from services.mileage_logs import MileageLogService
from services.scheduler_helper import sync_mileage_prompt_job
from services.service_items import ServiceItemService
from services.telegram_auth import TelegramAuthService

router = Router()


def get_app_keyboard(i18n: I18nContext) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    mini_app_url = settings.bot.mini_app_url
    if mini_app_url:
        builder.row(
            InlineKeyboardButton(
                text=i18n.get("open_app_button"),
                web_app=WebAppInfo(url=mini_app_url),
            )
        )
    if settings.domain:
        builder.row(
            InlineKeyboardButton(
                text=i18n.get("site_button"),
                url=f"https://{settings.domain}",
            )
        )
    return builder


@router.message(Command("start"))
@router.message(Command("app"))
async def cmd_start(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not message.from_user:
        return
    user_repo = UserRepository(session)
    auth_service = TelegramAuthService(session, user_repo)
    telegram_id = message.from_user.id

    if command.args:
        token = command.args.strip()
        try:
            result = await auth_service.link_user_by_token(token, telegram_id)
            if result:
                builder = get_app_keyboard(i18n)
                await message.answer(
                    i18n.get("start_linked_success"),
                    reply_markup=builder.as_markup() if builder.as_markup().inline_keyboard else None,
                )
            else:
                await message.answer(i18n.get("start_invalid_token"))

        except TelegramAlreadyLinkedError:
            builder = get_app_keyboard(i18n)
            await message.answer(
                i18n.get("start_already_linked"),
                reply_markup=builder.as_markup() if builder.as_markup().inline_keyboard else None,
            )
        except TelegramAlreadyLinkedToAnotherError:
            await message.answer(i18n.get("start_already_linked_to_another"))
        return

    user = await user_repo.get_by_telegram_id(telegram_id)

    if user:
        builder = get_app_keyboard(i18n)
        await message.answer(
            i18n.get(
                "start_welcome_back",
                name=html.quote(user.name),
            ),
            reply_markup=builder.as_markup() if builder.as_markup().inline_keyboard else None,
        )
    else:
        builder = InlineKeyboardBuilder()
        if settings.domain:
            builder.row(
                InlineKeyboardButton(
                    text=i18n.get("site_button"),
                    url=f"https://{settings.domain}",
                )
            )
        await message.answer(
            i18n.get("start_hello_new", name=html.quote(message.from_user.full_name)),
            reply_markup=builder.as_markup() if builder.as_markup().inline_keyboard else None,
        )

    return


@router.callback_query(F.data.startswith("mark_serviced:"))
async def on_mark_serviced_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not callback.data or not callback.message:
        return

    raw_id = callback.data.split(":", 1)[1]
    try:
        service_item_id = UUID(raw_id)
    except ValueError:
        return

    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer(i18n.get("language_not_linked"), show_alert=True)
        return

    service_repo = ServiceItemRepository(session)
    service_item = await service_repo.get_by_id(service_item_id)
    if not service_item:
        await callback.answer()
        return

    car_repo = CarRepository(session)
    mileage_repo = MileageLogRepository(session)
    reminder_repo = ReminderRepository(session)

    car = await car_repo.get_by_id(service_item.car_id)
    latest_mileage = await mileage_repo.get_latest_for_car(service_item.car_id)
    current_odometer = (
        latest_mileage.odometer_km
        if latest_mileage
        else (car.initial_odometer_km if car else service_item.last_service_odometer_km)
    )

    item_service = ServiceItemService(
        session=session,
        service_item_repository=service_repo,
        car_repository=car_repo,
        mileage_log_repository=mileage_repo,
        reminder_repository=reminder_repo,
    )

    await item_service.mark_serviced(
        service_item_id=service_item_id,
        mark_schema=ServiceItemMarkServiced(
            serviced_at=datetime.now(UTC),
            odometer_km=current_odometer,
        ),
        user_id=user.id,
    )

    success_msg = i18n.get("mark_service_done_success")
    await callback.answer(success_msg, show_alert=True)

    if isinstance(callback.message, Message):
        try:
            updated_text = f"{callback.message.html_text}\n\n<b>{success_msg}</b>"
            await callback.message.edit_text(text=updated_text, reply_markup=None)
        except Exception:
            pass


class MileagePromptState(StatesGroup):
    waiting_for_mileage = State()


@router.callback_query(F.data.startswith("skip_mileage:"))
async def on_skip_mileage_callback(
    callback: CallbackQuery,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not callback.data or not callback.message:
        return

    raw_id = callback.data.split(":", 1)[1]
    try:
        car_id = UUID(raw_id)
    except ValueError:
        return

    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer(i18n.get("language_not_linked"), show_alert=True)
        return

    car = await CarRepository(session).get_by_id(car_id)
    if not car:
        await callback.answer()
        return

    mileage_repo = MileageLogRepository(session)
    latest_log = await mileage_repo.get_latest_for_car(car_id)
    last_recorded = latest_log.created_at if latest_log else car.created_at

    sync_mileage_prompt_job(
        car, last_recorded, user.settings, already_prompted_today=True
    )

    skip_msg = i18n.get("skip_mileage_success")
    await callback.answer(skip_msg, show_alert=True)

    if isinstance(callback.message, Message):
        try:
            updated_text = f"{callback.message.html_text}\n\n<b>{skip_msg}</b>"
            await callback.message.edit_text(text=updated_text, reply_markup=None)
        except Exception:
            pass


@router.callback_query(F.data.startswith("prompt_mileage:"))
async def on_prompt_mileage_callback(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not callback.data or not callback.message:
        return

    raw_id = callback.data.split(":", 1)[1]
    try:
        car_id = UUID(raw_id)
    except ValueError:
        return

    user = await UserRepository(session).get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer(i18n.get("language_not_linked"), show_alert=True)
        return

    await state.set_state(MileagePromptState.waiting_for_mileage)
    await state.update_data(car_id=str(car_id))

    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer(i18n.get("prompt_mileage_enter_msg"))


@router.message(MileagePromptState.waiting_for_mileage)
async def on_mileage_input_message(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    i18n: I18nContext,
) -> None:
    if not message.from_user or not message.text:
        return

    user = await UserRepository(session).get_by_telegram_id(message.from_user.id)
    if not user:
        await state.clear()
        await message.answer(i18n.get("language_not_linked"))
        return

    data = await state.get_data()
    car_id_str = data.get("car_id")
    if not car_id_str:
        await state.clear()
        return

    try:
        car_id = UUID(car_id_str)
    except ValueError:
        await state.clear()
        return

    car_repo = CarRepository(session)
    mileage_repo = MileageLogRepository(session)
    car = await car_repo.get_by_id(car_id)

    if not car:
        await state.clear()
        return

    latest_log = await mileage_repo.get_latest_for_car(car_id)
    current_odometer = latest_log.odometer_km if latest_log else car.initial_odometer_km

    cleaned_text = message.text.replace(" ", "").replace("_", "").strip()
    try:
        new_km = int(cleaned_text)
        if new_km <= current_odometer or new_km <= 0:
            raise ValueError()
    except ValueError:
        await message.answer(
            i18n.get("prompt_mileage_invalid_msg", current_km=current_odometer)
        )
        return

    mileage_service = MileageLogService(
        session=session,
        car_repository=car_repo,
        mileage_log_repository=mileage_repo,
    )

    await mileage_service.add_mileage(
        create_schema=MileageLogCreate(
            car_id=car_id,
            odometer_km=new_km,
        ),
        user_id=user.id,
    )

    await state.clear()
    formatted_km = f"{new_km:,}".replace(",", " ")
    await message.answer(i18n.get("mileage_updated_success", new_km=formatted_km))
