# পালসার এআই ভার্সন ২.০ (PULSAR AI V2.0) — ক্রিপ্টো ফিউচারস ট্রেডিং প্ল্যাটফর্ম

**পালসার এআই V2.0** হলো একটি প্রাতিষ্ঠানিক মানের ক্লাউড-নেটিভ ক্রিপ্টো ফিউচারস অ্যানালাইসিস, সিগন্যাল জেনারেশন, ব্যাকটেস্টিং এবং পেপার ট্রেডিং প্ল্যাটফর্ম, যা **ICT (Inner Circle Trader)** এবং **SMC (Smart Money Concepts)** স্ট্র্যাটেজির ওপর ভিত্তি করে নির্মিত।

---

## ⚡ প্রধান বৈশিষ্ট্যসমূহ

- **মার্কেট ডেটা ইঞ্জিন**: **Binance USDⓈ-M Futures** (প্রাইমারি) এবং **Bybit Linear Perpetuals** (ফলব্যাক)। ক্লোজড ক্যান্ডেল ব্যবহার করে সিগন্যাল নিশ্চিতকরণ (Zero Repainting)।
- **ICT / SMC অ্যালগরিদম**:
  - সুইং ফ্র্যাক্টালস (Swing High / Swing Low) এবং ডিসপ্লেসমেন্ট ইমপালস (Displacement)।
  - মার্কেট স্ট্রাকচার শিফট (BOS - Break of Structure এবং CHoCH - Change of Character)।
  - লিকুইডিটি সুইপ (BSL, SSL, Equal Highs/Lows, এশিয়া/লন্ডন/নিউইয়র্ক সেশন হাই/লো)।
  - ফেয়ার ভ্যালু গ্যাপ (FVG, Inverse FVG, Mitigation ও Invalidation)।
  - অর্ডার ব্লক (Order Block) এবং ব্রেকার ব্লক (Breaker Block)।
  - প্রিমিয়াম ও ডিসকাউন্ট জোন এবং OTE (Optimal Trade Entry 0.62–0.79)।
- **কনফ্লুয়েন্স কোয়ালিটি গেট**: প্রতিটি সিগন্যালের মান ন্যূনতম ৭০/১০০ এবং রিস্ক-রিওয়ার্ড ন্যূনতম ১:২ হতে হবে। বাজার অস্পষ্ট থাকলে কোনো সিগন্যাল আসবে না (NO TRADE)।
- **রিস্ক ক্যালকুলেটর**: সঠিক পজিশন সাইজিং, মার্জিন, ফি ও স্লিপেজ এবং লিকুইডেশন দূরত্বের সতর্কতা।
- **ব্যাকটেস্টিং ইঞ্জিন**: ক্লোজড ক্যান্ডেল এবং বাস্তবসম্মত ফি ও স্লিপেজসহ নো-লুক-অ্যাহেড হিস্টোরিক্যাল ব্যাকটেস্টিং।
- **ভার্চুয়াল পেপার ট্রেডিং**: আসল অর্থের কোনো ঝুঁকি নেই। কোনো বাইন্যান্স প্রাইভেট এপিআই কী-এর প্রয়োজন হয় না।
- **টেলিগ্রাম বট নোটিফিকেশন**: নতুন সিগন্যাল, টিপি এবং স্টপ লস হিটের তাৎক্ষণিক পুশ নোটিফিকেশন।
- **১৩টি ড্যাশবোর্ড পেজ**: Next.js 14, React, TypeScript, Tailwind CSS এবং TradingView Lightweight Charts।

---

## 🚀 সহজ ক্লাউড ডিপ্লয়মেন্ট গাইড

আপনার কম্পিউটারে কোনো Python, Node.js বা Docker Desktop ইনস্টল করার প্রয়োজন নেই। সমস্ত সার্ভিস সরাসরি ক্লাউডে চলবে।

### ধাপ ১: গিটহাবে আপলোড
আপনার প্রজেক্টের সমস্ত ফাইল গিটহাব রিপোজিটরিতে পুশ করুন:
`https://github.com/alamgirhossain8918-dotcom/pulsar-ai`

### ধাপ ২: সুপাবেস (Supabase) ডেটাবেস সেটআপ
1. সুপাবেস ড্যাশবোর্ডে লগইন করুন।
2. **SQL Editor**-এ যান।
3. `supabase/migrations/20261103_init_pulsar_schema.sql` ফাইলের সব কোড পেস্ট করে **Run** করুন।
4. `supabase/seed.sql` ফাইলের কোড পেস্ট করে **Run** করুন।
5. **Project Settings** -> **Database** থেকে আপনার PostgreSQL সংযোগ লিংকটি কপি করে রাখুন।

### ধাপ ৩: রেলওয়ে (Railway) ব্যাকএন্ড ডিপ্লয়
1. [Railway.app](https://railway.app)-এ যান এবং GitHub রিপোজিটরিটি যুক্ত করুন।
2. Dockerfile হিসেবে `backend/Dockerfile` সিলেক্ট করুন।
3. Variables ট্যাবে `.env.example`-এর মতো আপনার Supabase `DATABASE_URL` যুক্ত করুন।
4. Settings থেকে ডোমেইন তৈরি করুন (যেমন: `https://pulsar-ai-production.up.railway.app`)।

### ধাপ ৪: ভার্সেল (Vercel) ফ্রন্টএন্ড ডিপ্লয়
1. [Vercel.com](https://vercel.com)-এ যান এবং `pulsar-ai` রিপোজিটরিটি ইম্পোর্ট করুন।
2. Root Directory হিসেবে `frontend` ফোল্ডার সিলেক্ট করুন।
3. Environment Variables-এ আপনার Railway ব্যাকএন্ড লিংকটি দিন:
   ```env
   NEXT_PUBLIC_API_URL=https://your-railway-app.up.railway.app/api/v1
   NEXT_PUBLIC_WS_URL=wss://your-railway-app.up.railway.app/api/v1/ws
   ```
4. **Deploy** বাটনে ক্লিক করুন। কয়েক মিনিটে আপনার পুরো ড্যাশবোর্ড লাইভ হয়ে যাবে!
