#!/bin/bash
# gunicorn -D -t 30 -w 1 -b 0.0.0.0:8763 'web_serve:app'
gunicorn -t 30 -w 1 -b 0.0.0.0:8763 'web_serve:app'