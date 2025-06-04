from django.contrib import admin
from . import models
# creating django file objects
from django.core.files import File

# zipprocessing
import zipfile
from django.conf import settings
import os
import shutil

import time

# Register your models here.

class TagAdmin(admin.ModelAdmin):

    search_fields = ['name']


class BuAdmin(admin.ModelAdmin):

    search_fields = ['name']


class PrototypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'bu', 'get_resource_no', 'get_tags', 'create_time', 'update_time', 'attachment', 'get_view_url')

    search_fields = ['name', 'bu__name']

    list_filter = [ 'bu__name', 'tags__name']


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('no', 'path', 'status', 'create_time', 'update_time', 'get_view_url')

    list_filter = ['status', 'prototype__name' ]
    exclude = ('url',)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            # 判断是否为更新操作
            if change:
                # 获取原始对象
                original_obj = models.Resource.objects.get(pk=obj.pk)
                # 保留原有的资源ID
                obj.no = original_obj.no
            else:
                # 新建资源时设置新的资源ID
                timestamp = int(round(time.time() * 1000))
                obj.no = timestamp
            if form.cleaned_data['path'] is not None:
                print(form.cleaned_data['path'])
                no = str(obj.no)  # 使用对象的no，而不是timestamp
                zip = zipfile.ZipFile(form.cleaned_data['path'])
                www_dir = os.path.join(settings.WWW_ROOT, no)
                
                # 如果是更新操作，先删除原有目录
                if change and os.path.exists(www_dir):
                    shutil.rmtree(www_dir)
                
                target_encoding = 'utf-8'
                if zip:
                    zip_file_name = str(zip.filename)
                    zip_file_name = zip_file_name[:zip_file_name.rfind(".")]
                    # 托管路径： www/压缩包名称/压缩包文件*
                    www_dir = os.path.join(www_dir, zip_file_name)
                    os.makedirs(www_dir)
                    for file in zip.namelist():
                        if file.startswith('.') or file.startswith('__MACOSX'):
                            continue
                        zip.extract(file, settings.MEDIA_ROOT)
                        # 处理加压后中文乱码
                        try:
                            right_file = file.encode('cp437').decode('utf-8')
                        except:
                            right_file = file.encode('cp437').decode('gbk')
                        shutil.move(os.path.join(settings.MEDIA_ROOT, file), os.path.join(www_dir, right_file))

                    obj.url = settings.WWW_URL + no + "/" + zip_file_name + "/" + zip_file_name + "/index.html"
                    print(obj.url)
                zip.close()
                
            super().save_model(request, obj, form, change)
            

admin.site.register(models.Prototype, PrototypeAdmin)

admin.site.register(models.Resource, ResourceAdmin)

admin.site.register(models.Tag, TagAdmin)

admin.site.register(models.Bu, BuAdmin)



admin.site.disable_action('delete_selected')