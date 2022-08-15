def update_data(cmd, data):
    if "data" not in cmd:
        cmd["data"] = data
    else:
        for fld in ["fields", "user"]:
            if fld in data:
                if fld not in cmd["data"]:
                    cmd["data"][fld] = data[fld]
                else:
                    for key in data[fld]:
                        cmd["data"][fld][key] = data[fld][key]
                
cmd = { "name": "fpga_ctrl",  "dir": "rmw", "data": {"fields": {"run": 1, "clear_statistics": 1, "clear_histogram": 1}, "user": {"par2": 200}}}
data = {"fields": {"run": 0}, "user": {"par1": 100}}
update_data(cmd, data)
print(cmd)

 