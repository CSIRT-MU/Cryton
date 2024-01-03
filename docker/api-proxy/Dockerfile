FROM httpd:2-alpine as api-proxy

LABEL authors="Jiri Raja <raja@ics.muni.cz>, Milan Bohacek <bohacek@ics.muni.cz>"

COPY docker/api-proxy/httpd.conf /usr/local/apache2/conf/httpd.conf
COPY docker/api-proxy/hp-vhosts.conf /usr/local/apache2/conf/extra/httpd-vhosts.conf
COPY static /usr/local/apache2/web/static

RUN chmod -R 755 /usr/local/apache2/web/static
