#!/bin/bash

uv run resume_md/main.py --input ./example/ats_info_test.md --output ./example/ats_info_test.html
uv run resume_md/main.py --input ./example/example1.md --output ./example/example1.html
uv run resume_md/main.py --input ./example/example2.md --output ./example/example2.html
uv run resume_md/main.py --input ./example/page_break_test.md --output ./example/page_break_test.html