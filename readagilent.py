
from pathlib import Path
import struct 
import numpy as np
import matplotlib.pyplot as plt


#data_folder = Path(r'C:\Users\clasc\Downloads\HH081 NaphBpin deboronation base screen 2022-03-13 16-51-04\HH081 NaphBpin deboronation base screen 2022-03-13 16-51-04\001-HH081-10-00-P1-C8.D')
data_folder = Path(r'C:\Users\clasc\Downloads\HH081 NaphBpin deboronation base screen 2022-03-13 16-51-04\HH081 NaphBpin deboronation base screen 2022-03-13 16-51-04\002-HH081-10-01-P1-B1.D')

uv_file = data_folder/'DAD1.UV'


with open(uv_file, 'rb') as f:
    sample_name_pos = 0x35A                                 #sample name position
    scan_num_pos = 0x116                                    #scan number info at position 0x116
    wavelength_pos = 0x1008                                 #1st wavelength info starts at position 0x1008
    sp_info_pos = 0x1002                                    #1st spectrum info starts at position 0x1002
    sp_data_pos = 0x1016                                    #1st spectrum data starts at position 0x1016

    f.seek(sample_name_pos)                                 #goto position of sample name
    read_len = struct.unpack('>B', f.read(1))[0]            #read length of sample to read
    sample_name_tmp = f.read(2*read_len-1).decode('ascii').strip()  #for some reason, direct reading includes some nonprintable characters, remove in next line
    sample_name = ''.join(x for x in sample_name_tmp if x.isprintable())

    f.seek(scan_num_pos)
    nscans = struct.unpack('>i', f.read(4))[0]              #get number of scans,for some reason, it reads 0x00000701 to be 1794, while should be 1793
    
    f.seek(wavelength_pos)
    nm_start = struct.unpack('<H', f.read(2))[0] / 20       #start wavelength
    nm_end = struct.unpack('<H', f.read(2))[0] / 20         #end wavelength
    nm_step = struct.unpack('<H', f.read(2))[0] / 20        #wavelength step
    wavelength_num = int((nm_end - nm_start) / nm_step)
    uv_data = np.zeros((nscans, wavelength_num+1))          #create array to store uv 3d data

    for i in range (0,nscans):
        f.seek(sp_info_pos)                                 #goto position of current spectrum info
        step = struct.unpack('<H', f.read(2))[0]            #get data length of current spectrum
        sp_info_pos += step                                 #update the next spectrum info position
        uv_data[i,0] = struct.unpack('<L', f.read(4))[0] / 60000 #get time by minute

        uv_int = 0                                          #re-set uv intensity
        f.seek(sp_data_pos)                                 #goto position of current spectrum data
        sp_data_pos += step                                 #update the next spectrum data position
        for j in range (0, wavelength_num):
            uv_tmp = struct.unpack('<h', f.read(2))[0]      #read uv intensity as short int (2 bytes)
            if uv_tmp != -32768:                            
                uv_int += uv_tmp / 2000                     # DO NOT change "+=" to "="! it will go wild!                
            else:                                           #short int saturated, use int (following 4 bytes)
                uv_int = struct.unpack('<i', f.read(4))[0] / 2000    
            uv_data[i,j+1] = uv_int                         #write to uv_data array

uv_data_header = 'time,'                                    #create header for csv file, time, then each wavelength
for i in range (0, wavelength_num):
    uv_data_header += (str(nm_start + i * nm_step) + ',')

out_csv = sample_name + '.csv'
np.savetxt(out_csv, uv_data, delimiter = ',', header = uv_data_header)
#plt.plot(uv_data[:,0], uv_data[:,31])
#plt.show()
