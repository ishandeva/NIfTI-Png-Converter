from django.shortcuts import render
from .forms import SharingForms
from django.conf import settings
from tempfile import TemporaryFile 
from django.http import HttpResponse
import imageio,nibabel,numpy
from zipfile import ZipFile

import os,shutil
from pathlib import Path


# Create your views here

def index(request):
    if request.method == 'POST':
        form = SharingForms(request.POST, request.FILES)
        
        if(form.is_valid()):
            for f in request.FILES.getlist('file'):
                file = f
                filename = f.name
                filename, file_extension = os.path.splitext(filename)
                path = file.temporary_file_path()
                outputpath = os.path.join(settings.MEDIA_ROOT,filename)
                image_array = nibabel.load(path).get_fdata()
                response = HttpResponse(content_type='application/zip')
                zip_file = ZipFile(response, 'w')
                
                if len(image_array.shape) == 4:
                    # set 4d array dimension values
                    nx, ny, nz, nw = image_array.shape
                    total_volumes = image_array.shape[3]
                    total_slices = image_array.shape[2] 
                    for current_volume in range(0, total_volumes):
                        slice_counter = 0
                        for current_slice in range(0, total_slices):
                            if (slice_counter % 1) == 0:
                                data = image_array[:, :, current_slice, current_volume]
                                image_name = filename[:-4] + "_t" + "{:0>3}".format(str(current_volume+1)) + "_z" + "{:0>3}".format(str(current_slice+1))+ ".png"
                                imageio.imwrite(image_name, data)
                                zip_file.write(image_name)
                                src = image_name
                                if not os.path.exists(outputpath):
                                    os.makedirs(outputpath)
                                shutil.move(src, outputpath)
                                slice_counter += 1


                elif len(image_array.shape) == 3:
                    # set 4d array dimension values
                    nx, ny, nz = image_array.shape
                    total_slices = image_array.shape[2]
                    slice_counter = 0
                    for current_slice in range(0, total_slices):
                        if (slice_counter % 1) == 0:
                            data = image_array[:, :, current_slice]
                            image_name = filename[:-4] + "_z" + "{:0>3}".format(str(current_slice+1))+ ".png"
                            imageio.imwrite(image_name, data)
                            zip_file.write(image_name)
                            src = image_name
                            if not os.path.exists(outputpath):
                                os.makedirs(outputpath)
                            shutil.move(src, outputpath)
                            slice_counter += 1
                            
            
                shutil.rmtree(outputpath)   
                zip_file.close()    
                response['Content-Disposition'] = 'attachment; filename={}'.format(filename)+".zip"  
                return response
    form = SharingForms()
    return render(request,'index.html',{'form':form})
