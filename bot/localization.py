"""User-facing texts for the Telegram MVP."""

from __future__ import annotations

LANGUAGES = {"ru": "Русский", "uz": "O‘zbekcha", "en": "English"}
DEFAULT_LANGUAGE = "ru"

MESSAGES = {
    "ru": {
        "welcome": "Я ScamShield — помощник по проверке подозрительных сообщений, ссылок, чеков и файлов.",
        "help": "Отправьте текст, ссылку, изображение или файл. Я оценю риск и подскажу безопасное действие. Команда /language меняет язык.",
        "choose_language": "Выберите язык интерфейса:",
        "language_saved": "Язык интерфейса: {language}.",
        "processing": "Проверяю. Это может занять до 30 секунд…",
        "unsupported": "Этот формат пока не поддерживается. Отправьте текст, ссылку, изображение, PDF, DOC/DOCX, ZIP/RAR или аудиофайл.",
        "too_large": "Файл слишком большой. Максимальный размер — {limit_mb} МБ.",
        "too_long": "Текст слишком длинный для проверки. Сократите его и повторите попытку.",
        "failed": "Не удалось завершить проверку. Не открывайте подозрительный файл и повторите попытку позже.",
        "result": "<b>Результат проверки: {risk}</b>\n\n{summary}\n\n<b>Рекомендация:</b> {recommendation}",
        "low": "Безопасно",
        "medium": "Нужна осторожность",
        "high": "Высокий риск",
        "critical": "Опасно",
        "unknown": "Не удалось определить",
        "recommend_low": "Сохраняйте осторожность: проверяйте отправителя и не передавайте коды из SMS.",
        "recommend_medium": "Не переходите по ссылкам и проверьте информацию через официальный канал организации.",
        "recommend_high": "Не открывайте ссылку или вложение, не сообщайте пароли, коды и данные карты.",
        "recommend_critical": "Не взаимодействуйте с содержимым. При необходимости сообщите в банк или службу поддержки платформы.",
        "recommend_unknown": "Не открывайте файл и проверьте его через официальный канал отправителя.",
        "disclaimer": "ScamShield — информационный помощник, а не банк, антивирус или юридическая консультация. Оценка не гарантирует безопасность.",
        "start_notice": "Перед использованием не отправляйте пароли, коды из SMS, данные карт, паспортные данные или чужие личные переписки. Условия обработки: /privacy.",
        "privacy": "<b>Условия использования и конфиденциальность (пилот)</b>\n\nScamShield даёт автоматическую вспомогательную оценку риска. Он не подтверждает факт мошенничества, не гарантирует безопасность и не заменяет проверку через банк, государственный орган или специалиста. Не принимайте решение о переводе денег только по ответу бота.\n\n<b>Что можно отправлять</b>\nТолько материалы, на обработку которых у вас есть право: свои сообщения, ссылки, файлы или обезличенные примеры. Не отправляйте пароли, коды подтверждения, данные банковских карт, паспортные данные, биометрию, медицинские данные и чужие личные переписки без согласия.\n\n<b>Как обрабатываются материалы</b>\nФайлы временно скачиваются для проверки и удаляются после неё. Для анализа текста или изображений, в зависимости от настроек бота, материал может обрабатываться выбранным внешним AI-провайдером. Не отправляйте чувствительные данные.\n\n<b>Если есть риск</b>\nНе переходите по ссылке, не открывайте вложение и свяжитесь с банком или сервисом только через официальный канал.\n\nПродолжая пользоваться ботом после этого уведомления, вы подтверждаете, что понимаете эти ограничения. Контакт по вопросам: {support_contact}.",
    },
    "uz": {
        "welcome": "Men ScamShield — shubhali xabarlar, havolalar, cheklar va fayllarni tekshirish yordamchisiman.",
        "help": "Matn, havola, rasm yoki fayl yuboring. Men xavfni baholayman va xavfsiz harakatni tavsiya qilaman. Tilni /language bilan o‘zgartiring.",
        "choose_language": "Interfeys tilini tanlang:",
        "language_saved": "Interfeys tili: {language}.",
        "processing": "Tekshirilyapti. Bu 30 soniyagacha davom etishi mumkin…",
        "unsupported": "Bu format hali qo‘llab-quvvatlanmaydi. Matn, havola, rasm, PDF, DOC/DOCX, ZIP/RAR yoki audio fayl yuboring.",
        "too_large": "Fayl juda katta. Maksimal hajm — {limit_mb} MB.",
        "too_long": "Matn tekshiruv uchun juda uzun. Uni qisqartirib, qayta yuboring.",
        "failed": "Tekshiruvni tugatib bo‘lmadi. Shubhali faylni ochmang va keyinroq urinib ko‘ring.",
        "result": "<b>Tekshiruv natijasi: {risk}</b>\n\n{summary}\n\n<b>Tavsiya:</b> {recommendation}",
        "low": "Xavfsiz",
        "medium": "Ehtiyot bo‘ling",
        "high": "Yuqori xavf",
        "critical": "Xavfli",
        "unknown": "Aniqlab bo‘lmadi",
        "recommend_low": "Ehtiyotkor bo‘ling: jo‘natuvchini tekshiring va SMS kodlarini bermang.",
        "recommend_medium": "Havolaga o‘tmang, ma’lumotni tashkilotning rasmiy kanali orqali tekshiring.",
        "recommend_high": "Havola yoki faylni ochmang, parol, kod va karta ma’lumotlarini bermang.",
        "recommend_critical": "Kontent bilan ishlamang. Zarur bo‘lsa bank yoki platforma yordam xizmatiga xabar bering.",
        "recommend_unknown": "Faylni ochmang va jo‘natuvchini rasmiy kanal orqali tekshiring.",
        "disclaimer": "ScamShield axborot yordamchisi bo‘lib, bank, antivirus yoki yuridik maslahat o‘rnini bosa olmaydi. Baho xavfsizlikni kafolatlamaydi.",
        "start_notice": "Parol, SMS kodlari, karta yoki pasport ma’lumotlari va boshqa odamlarning shaxsiy yozishmalarini yubormang. Qayta ishlash shartlari: /privacy.",
        "privacy": "<b>Foydalanish va maxfiylik shartlari (pilot)</b>\n\nScamShield xavfni avtomatik yordamchi tarzda baholaydi. U firibgarlik faktini tasdiqlamaydi, xavfsizlikni kafolatlamaydi va bank, davlat organi yoki mutaxassis tekshiruvini almashtirmaydi. Pul o‘tkazish haqida faqat bot javobi asosida qaror qabul qilmang.\n\n<b>Nimani yuborish mumkin</b>\nFaqat qayta ishlash huquqiga ega bo‘lgan materiallarni: o‘z xabarlaringiz, havolalaringiz, fayllaringiz yoki shaxsiy ma’lumotsiz misollarni yuboring. Parol, tasdiqlash kodi, karta ma’lumotlari, pasport ma’lumotlari, biometrik yoki tibbiy ma’lumotlar hamda roziliksiz boshqa odamlarning yozishmalarini yubormang.\n\n<b>Materiallar qanday qayta ishlanadi</b>\nFayllar tekshirish uchun vaqtincha yuklanadi va undan keyin o‘chiriladi. Bot sozlamasiga qarab, matn yoki rasm tanlangan tashqi AI-provayder tomonidan qayta ishlanishi mumkin. Maxfiy ma’lumot yubormang.\n\n<b>Xavf bo‘lsa</b>\nHavolaga o‘tmang, faylni ochmang va bank yoki servis bilan faqat rasmiy kanal orqali bog‘laning.\n\nUshbu bildirishnomadan keyin botdan foydalanishni davom ettirish orqali siz bu cheklovlarni tushunganingizni tasdiqlaysiz. Savollar uchun aloqa: {support_contact}.",
    },
    "en": {
        "welcome": "I am ScamShield — a helper for checking suspicious messages, links, receipts, and files.",
        "help": "Send text, a link, an image, or a file. I will assess the risk and suggest a safe next step. Use /language to change the language.",
        "choose_language": "Choose an interface language:",
        "language_saved": "Interface language: {language}.",
        "processing": "Checking the content. This can take up to 30 seconds…",
        "unsupported": "This format is not supported yet. Send text, a link, an image, PDF, DOC/DOCX, ZIP/RAR, or an audio file.",
        "too_large": "The file is too large. The maximum size is {limit_mb} MB.",
        "too_long": "The text is too long to analyse. Shorten it and try again.",
        "failed": "The check could not be completed. Do not open the suspicious file and try again later.",
        "result": "<b>Check result: {risk}</b>\n\n{summary}\n\n<b>Recommendation:</b> {recommendation}",
        "low": "Safe",
        "medium": "Use caution",
        "high": "High risk",
        "critical": "Dangerous",
        "unknown": "Could not determine",
        "recommend_low": "Stay cautious: verify the sender and never share SMS verification codes.",
        "recommend_medium": "Do not follow links; verify the information through the organisation's official channel.",
        "recommend_high": "Do not open the link or attachment and do not share passwords, codes, or card details.",
        "recommend_critical": "Do not interact with the content. Contact your bank or the platform support team if needed.",
        "recommend_unknown": "Do not open the file; verify the sender through an official channel.",
        "disclaimer": "ScamShield is an informational helper, not a bank, antivirus, or legal adviser. Its assessment does not guarantee safety.",
        "start_notice": "Do not send passwords, SMS codes, card or passport data, or anyone else's private correspondence. Processing terms: /privacy.",
        "privacy": "<b>Terms of use and privacy notice (pilot)</b>\n\nScamShield provides an automated assistive risk assessment. It does not confirm fraud, guarantee safety, or replace verification through a bank, public authority, or security professional. Do not make a payment decision based only on the bot response.\n\n<b>What you may send</b>\nSend only materials you have the right to process: your own messages, links, files, or anonymised examples. Do not send passwords, verification codes, bank-card or passport data, biometric or medical data, or anyone else's private correspondence without consent.\n\n<b>How materials are processed</b>\nFiles are downloaded temporarily for analysis and deleted afterwards. Depending on the bot configuration, text or images may be processed by a selected external AI provider. Do not send sensitive data.\n\n<b>If there is a risk</b>\nDo not follow the link or open the attachment. Contact the bank or service only through its official channel.\n\nBy continuing to use the bot after this notice, you confirm that you understand these limitations. Support contact: {support_contact}.",
    },
}


def text(language: str, key: str, **values: str) -> str:
    """Return a localised message, safely falling back to Russian."""
    return MESSAGES.get(language, MESSAGES[DEFAULT_LANGUAGE])[key].format(**values)
