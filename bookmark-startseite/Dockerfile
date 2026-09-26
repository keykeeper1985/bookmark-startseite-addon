ARG BUILD_FROM
FROM ${BUILD_FROM}

ENV PYTHONUNBUFFERED=1 \
    PORT=8099 \
    BOOKMARKS_FILE=/config/bookmark-startseite/bookmarks.json

WORKDIR /app
COPY app/ /app/
RUN mkdir -p /config/bookmark-startseite

EXPOSE 8099
CMD ["python3", "server.py"]
