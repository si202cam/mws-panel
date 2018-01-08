# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-04 17:07
from __future__ import unicode_literals

from django.db import migrations, models

php_lib_mappings = [
    ('libawl-php', 'libawl-php'),
    ('libgv-php5', 'libgvc6'),
    ('libmarkdown-php', 'libmarkdown-php'),
    ('libnusoap-php', 'libnusoap-php'),
    ('libownet-php', 'libownet-php'),
    ('php5-adodb', 'libphp-adodb'),
    ('php5-dev', 'php-all-dev'),
    ('php5-sasl', 'php-auth-sasl'),
    ('php5-cgi', 'php-cgi'),
    ('php5-enchant', 'php-enchant'),
    ('php5-fpm', 'php-fpm'),
    ('php5-xsl', 'php-fxsl'),
    ('php5-gearman', 'php-gearman'),
    ('php5-geoip', 'php-geoip'),
    ('php5-gmp', 'php-gmp'),
    ('php5-gnupg', 'php-gnupg'),
    ('php5-igbinary', 'php-igbinary'),
    ('php5-imagick', 'php-imagick'),
    ('php5-imap', 'php-imap'),
    ('php5-interbase', 'php-interbase'),
    ('php5-intl', 'php-intl'),
    ('php5-libvirt-php', 'php-libvirt-php'),
    ('php5-mcrypt', 'php-mcrypt'),
    ('php5-memcache', 'php-memcache'),
    ('php5-memcached', 'php-memcached'),
    ('php5-mongo', 'php-mongodb'),
    ('php5-msgpack', 'php-msgpack'),
    ('php5-oauth', 'php-oauth'),
    ('php5-odbc', 'php-odbc'),
    ('php5-pecl-http', 'php-pecl-http'),
    ('php5-pecl-http-dev', 'php-pecl-http-dev'),
    ('php5-pgsql', 'php-pgsql'),
    ('php5-dbg', 'php-phpdbg'),
    ('php5-phpdbg', 'php-phpdbg'),
    ('php5-pinba', 'php-pinba'),
    ('php5-propro', 'php-propro'),
    ('php5-propro-dev', 'php-propro-dev'),
    ('php5-pspell', 'php-pspell'),
    ('php5-radius', 'php-radius'),
    ('php5-raphf', 'php-raphf'),
    ('php5-raphf-dev', 'php-raphf-dev'),
    ('php5-recode', 'php-recode'),
    ('php5-redis', 'php-redis'),
    ('php5-remctl', 'php-remctl'),
    ('php5-rrd', 'php-rrd'),
    ('php5-snmp', 'php-snmp'),
    ('php5-solr', 'php-solr'),
    ('php5-ssh2', 'php-ssh2'),
    ('php5-stomp', 'php-stomp'),
    ('php5-sybase', 'php-sybase'),
    ('php5-tidy', 'php-tidy'),
    ('php5-twig', 'php-twig'),
    ('php5-xdebug', 'php-xdebug'),
    ('php5-xmlrpc', 'php-xmlrpc'),
    ('php5-yac', 'php-yac'),
    ('php5-zmq', 'php-zmq'),
    ('php5-apcu', 'php5-apcu'),
]


def populate_name_next_os(apps, schema_editor):
    PHPLib = apps.get_model('apimws', 'PHPLib')
    for mapping in php_lib_mappings:
        php_lib = PHPLib.objects.get(name=mapping[0])
        php_lib.name_next_os = mapping[1]
        php_lib.save()


class Migration(migrations.Migration):

    dependencies = [
        ('apimws', '0010_auto_20160506_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='phplib',
            name='name_next_os',
            field=models.CharField(blank=True, null=True, max_length=150),
        ),
        migrations.RunPython(populate_name_next_os),
    ]
