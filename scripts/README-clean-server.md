# 🧹 clean-server

**Automated server cleanup & maintenance script**

`clean-server` هو سكربت Bash مخصص لتنظيف السيرفر بشكل آمن ومنهجي، ويُستخدم عادةً عبر **cron** للحفاظ على المساحة والأداء دون تدخل يدوي.

---

## ✨ المميزات

- 🧹 تنظيف مخلفات النظام (APT)
- 🧾 تقليص حجم سجلات `journalctl`
- 🐳 تنظيف Docker (إن وُجد)
- 🗑️ تنظيف مجلدات `/tmp` و `/var/tmp`
- 👤 تنظيف كاش المستخدم
- 📦 إدارة النسخ الاحتياطية:
  - الاحتفاظ بآخر **نسختين فقط**
  - حذف النسخ الأقدم تلقائيًا
- 📝 تسجيل كامل للعمليات في ملف Log

---

## 📁 المسارات التي يتعامل معها

| المسار | الغرض |
|------|------|
| `/var/backups/server` | نسخ احتياطية كاملة للسيرفر |
| `/var/backups/sites` | نسخ احتياطية للمواقع |
| `/tmp` – `/var/tmp` | ملفات مؤقتة |
| `/home/tamer/.cache` | كاش المستخدم |
| `/var/log/clean-server.log` | سجل التنفيذ |

---

## 🚀 التشغيل اليدوي

```bash
sudo /usr/local/bin/clean-server
```

---

## ⏰ الجدولة (Cron)

```cron
0 5 * * * /usr/local/bin/clean-server >> /var/log/clean-server-cron.log 2>&1
```

---

## 🧾 السجلات

- `/var/log/clean-server.log`
- `/var/log/clean-server-cron.log`

---

## ⚠️ ملاحظات

- لا يحذف ملفات تشغيلية أو قواعد بيانات
- آمن للاستخدام اليومي
- مخصص لسيرفرات الإنتاج

---

## 👨‍💻 المؤلف

**Tamer Hamad Faour**  
pi-node-server-infra
