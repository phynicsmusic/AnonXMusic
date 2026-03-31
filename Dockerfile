# ၁။ Python 3.13 Slim version ကို အခြေခံထားသည်
FROM python:3.13-slim

# ၂။ အလုပ်လုပ်မည့် Folder သတ်မှတ်ခြင်း
WORKDIR /app

# ၃။ လိုအပ်သော Linux Software များအား ပိုမိုလုံခြုံစွာ တပ်ဆင်ခြင်း
RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    unzip \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ၄။ Deno ကို | sh (Direct Pipe) မသုံးဘဲ အဆင့်ဆင့် တပ်ဆင်ခြင်း
# ဤနည်းလမ်းသည် အင်တာနက်မှ script ကို တိုက်ရိုက် run ခြင်းထက် ပိုမိုလုံခြုံသည်
RUN curl -fsSL https://deno.land/install.sh -o install_deno.sh \
    && sh install_deno.sh \
    && rm install_deno.sh

# ၅။ Deno Path လမ်းကြောင်း သတ်မှတ်ခြင်း
ENV DENO_INSTALL="/root/.deno"
ENV PATH="${DENO_INSTALL}/bin:${PATH}"

# ၆။ Python Libraries များအား Cache မသိမ်းဘဲ တပ်ဆင်ခြင်း (File size သေးစေရန်)
COPY requirements.txt .
RUN pip3 install --no-cache-dir -U pip \
    && pip3 install --no-cache-dir -U -r requirements.txt

# ၇။ Bot Code များအားလုံးကို ကူးယူခြင်း
COPY . .

# ၈။ Bot ကို စတင်မောင်းနှင်ခြင်း
CMD ["bash", "start"]
