import commands as cm
import reader

# Try these:
#cm.send_raw("f1f2f306010108f4f5f6") # Turn on
cm.send_raw("f1f2f306010007f4f5f6") # Turn off
reader.show(reader.extract_json_from_response(cm.send_raw("f1f2f3000000f4f5f6"))) # Media list/refresh
exit(1)

#send_raw("f1f2f3000000f4f5f6")  # Media list/refresh
#reader.show(reader.extract_json_from_response(cm.send_raw("f1f2f3000000f4f5f6"))) # Media list/refresh
#cm.send_raw(cm.media_play_command(6))

#send_raw(angle_cmd(0)) # Angle ctrl

#cm.send_raw(cm.delete_file_cmd(0))
#reader.show(reader.extract_json_from_response(cm.send_raw("f1f2f3000000f4f5f6")))

cm.send_raw("aa00000002f000a5")

#cm.send_raw("f1f2f30c000cf4f5f6") #Dunno
cm.send_raw("f1f2f30c000cf4f5f6") # Dunno

cm.send_raw("f1f2f3130013f4f5f6") # account
cm.send_raw("f1f2f3120012f4f5f6") # MCU
cm.send_raw("f1f2f32c002cf4f5f6") # CS_Box
cm.send_raw("f1f2f3000000f4f5f6") # Media list

#cm.send_raw("f1f2f301010608f4f5f6")

cm.send_raw(cm.build_bulk_config({"0": "0"}))
cm.send_raw("f1f2f3000000f4f5f6") # Media list





#send_raw("f1f2f30401070cf4f5f6") # [7] muoon.mp4
#send_raw("f1f2f30401060bf4f5f6") # [6] saku_PIC.mp4