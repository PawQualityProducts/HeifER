import isobmff

media_file = isobmff.MediaFile()

#sample apple iphone file
media_file.read('IMG_3802.HEIC')                       #ok

#Nokia sample files
#media_file.read('C001.heic')                           #ok
#media_file.read('bothie_1440x960.heic')                #problem at 843
#media_file.read('cheers_1440x960.heic')                #ok
#media_file.read('crowd_1440x960.heic')                 #ok
#media_file.read('grid_960x640.heic')                   #ok
#media_file.read('grid_960x640.heic')                   #ok
#media_file.read('lights_1440x960.heic')                #problem at 500,512
#media_file.read('old_bridge_1440x960.heic')            #ok
#media_file.read('overlay_1000x680.heic')               #ok
#media_file.read('rally_burst.heic')                    #problem at 1934,1946
#media_file.read('random_collection_1440x960.heic')     #ok
#media_file.read('sea1_animation.heic')                 #problem at 1649
#media_file.read('season_collection_1440x960.heic')     #problem at 1477
#media_file.read('ski_jump_1440x960.heic')              #ok
#media_file.read('spring_1440x960.heic')                #ok
#media_file.read('starfield_animation.heic')            #probme at 1649
#media_file.read('stereo_1200x800.heic')                #problem at 845
#media_file.read('summer_1440x960.heic')                #ok
#media_file.read('surfer_1440x960.heic')                #ok
#media_file.read('winter_1440x960.heic')                #ok

print(media_file)


