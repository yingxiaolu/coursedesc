FROM python:3.9

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt
RUN pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu117
# COPY  dist/chatgpt_serve-1.1.2-py3-none-any.whl /app/chatgpt_serve-1.1.2-py3-none-any.whl

# RUN pip install -U pip && pip install chatgpt_serve-1.1.2-py3-none-any.whl

# RUN rm -rfv /app/chatgpt_serve-1.1.2-py3-none-any.whl
