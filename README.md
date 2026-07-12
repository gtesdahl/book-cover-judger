---
title: Book Cover Judger
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: mit
app_port: 7860
---

# Book Cover Judger

Upload a book cover image and predict its popularity (High, Medium, or Low) using a ResNet34 CNN trained with fastai on Goodreads data.

Built as a capstone project for the Machine Learning Guild Apprentice Program.

## Local development

```bash
docker build -t book-cover-judger .
docker run --rm -p 7860:7860 book-cover-judger
```

Open http://localhost:7860

## Original repository

[github.com/gtesdahl/book-cover-judger](https://github.com/gtesdahl/book-cover-judger)
