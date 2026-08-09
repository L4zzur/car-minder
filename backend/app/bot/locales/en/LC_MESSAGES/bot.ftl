start_linked_success =
    🎉 <b>account successfully linked!</b>

    now you can use the telegram mini app and get notifications.

start_invalid_token =
    ❌ <b>invalid link token.</b>

    looks like the link expired (5 minutes). generate a new one on the website.

start_already_linked = ⚠️ your profile on the website is already linked to telegram.

start_already_linked_to_another = ⚠️ this telegram account is already linked to another user.

start_welcome_back =
    👋 <b>welcome back, { $name }!</b>

    your account is linked and ready to go.

start_hello_new =
    👋 <b>hi, { $name }!</b>

    to start using car minder:
    1. register on the website.
    2. open your profile and press <b>“link telegram”</b>.

site_button = website

language_prompt = 🌐 pick the language for notifications and the bot:

language_changed = ✅ language saved: { $language }

language_not_linked =
    ⚠️ first link your account: open the website, go to “profile” and press “link telegram”.

language_name_ru = 🇷🇺 русский
language_name_en = 🇬🇧 english

service_reminder_title = 🔧 <b>time for service: { $car_brand } { $car_model }</b>
service_reminder_item = 📍 <b>service item:</b> { $item_name }
service_reminder_reason_days = ⏳ days left until service: <b>{ $days_left }</b>
service_reminder_reason_km = 🚗 km left until service: <b>{ $km_left }</b>
service_reminder_overdue = ⚠️ <b>service is due!</b>
mark_service_done_button = ✅ mark service completed
mark_service_done_success = ✅ service marked as completed!

mileage_prompt_title = 🚙 <b>odometer update: { $car_brand } { $car_model }</b>
mileage_prompt_body = you haven't updated your mileage for <b>{ $days }</b> days (current: <b>{ $current_km }</b> km). what's the odometer now?
update_mileage_button = ✍️ enter new mileage
skip_mileage_button = ⏩ skip
skip_mileage_success = ⏩ mileage reminder skipped. will remind next time!
prompt_mileage_enter_msg = ✏️ <b>enter new mileage as a number</b> in reply message (e.g. 125500):
prompt_mileage_invalid_msg = ❌ invalid value. odometer reading must be a number greater than current ({ $current_km } km).
mileage_updated_success = ✅ odometer <b>{ $new_km }</b> km successfully saved!
