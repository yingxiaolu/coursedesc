#!/bin/bash
gunicorn -D -t 30 -w 1 -b 0.0.0.0:8762 'web_serve:app'
