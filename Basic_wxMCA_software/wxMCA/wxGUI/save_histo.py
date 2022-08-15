import os
import json
import csv

def export_to_files(mca_id, out_dict, selection, pathname, data_path, file_name):
    if selection == 0:
        with open(pathname, 'w+') as fout:
            fout.write(json.dumps(out_dict)+'\n')
        with open(data_path + '/' + file_name, 'w+') as fout:
            fout.write(json.dumps(out_dict)+'\n')

    elif selection == 1:
        histo_csv_file = open(pathname, 'w+', newline = '')
        with histo_csv_file:
            histo_csv_writer = csv.writer(histo_csv_file)
            if mca_id in [0x201, 0x101, 0x102, 0x202]:
                histo_data = out_dict["histo"]["fields"]["histogram"]
            elif mca_id in [0x203, 0x103, 0x6001]:
                histo_data = out_dict["histo"]["registers"]
            histo_csv_writer.writerow(["KeV","Counts"])
            for i, data in enumerate(histo_data):
                histo_csv_writer.writerow([i*2, data])

        rates_csv_file = open(pathname.replace("histogram", "rates"), 'w+', newline = '')
        with rates_csv_file:
            rates_csv_writer = csv.writer(rates_csv_file)
            if mca_id in [0x203, 0x103, 0x6001]:
                for key, value in out_dict['rates']['user']['bank_0'].items():
                    rates_csv_writer.writerow([key, value])
            elif mca_id in [0x201, 0x101, 0x102, 0x202]:
                for key, value in out_dict['arm_status']['fields'].items():
                    rates_csv_writer.writerow([key, value])

    elif selection == 2:
        xml_template_path = os.path.dirname(os.getcwd()) + "\wxGUI\controls"
        if mca_id in [0x201, 0x101]:
            xml_template_file = xml_template_path + "\sample_mca_1k.xml"
            arm_keys = ["arm_build", "voltage_target", "avg_temperature", "trigger_threshold"]
        elif mca_id in [0x102, 0x202]:
            xml_template_file = xml_template_path + "\sample_mca_2k.xml"
            arm_keys = ["arm_build", "voltage_target", "avg_temperature", "trigger_threshold"]
        elif mca_id in [0x203, 0x103]:
            xml_template_file = xml_template_path + "\sample_mca_3k.xml"
            arm_keys = ["arm_build", "fpga_build", "voltage_target", "avg_temperature"]
            fpga_keys = ["adc_sr", "pulse_threshold", "impedance", "integration_time", "digital_gain"]
        elif mca_id in [0x6001]:
            xml_template_file = xml_template_path + "\sample_mca_emorpho.xml"
            fpga_keys = ["high_voltage", "temperature", "pulse_threshold", "adc_sr", "impedance", "integration_time", "digital_gain"]

        with open(xml_template_file, 'r') as fin:
            xml_template = fin.read()
        xml_template = xml_template.replace("serial_number", out_dict["serial_number"])
        xml_template = xml_template.replace("mca_id_str", out_dict["mca_id_str"])
        for pri_key in out_dict.keys():
            if pri_key.startswith("arm"):
                for sec_key in out_dict[pri_key]["fields"].keys():
                    if sec_key in arm_keys:
                        xml_template = xml_template.replace(sec_key, str(out_dict[pri_key]["fields"][sec_key]))
            elif pri_key.startswith("fpga"):
                for sec_key in out_dict[pri_key]["user"].keys():
                    if sec_key in fpga_keys:
                        xml_template = xml_template.replace(sec_key, str(out_dict[pri_key]["user"][sec_key]))
            elif pri_key.startswith("histo"):
                if mca_id in [0x201, 0x101, 0x102, 0x202]:
                    xml_template = xml_template.replace("histogram", ' '.join([str(i) for i in out_dict[pri_key]["fields"]["histogram"]]))
                elif mca_id in [0x203, 0x103, 0x6001]:
                    xml_template = xml_template.replace("histogram", ' '.join([str(i) for i in out_dict[pri_key]["registers"]]))
            elif pri_key.startswith("rates"):
                if mca_id in [0x203, 0x103, 0x6001]:
                    xml_template = xml_template.replace("run_time", str(out_dict[pri_key]['user']['bank_0']['run_time']))
                elif mca_id in [0x201, 0x101, 0x102, 0x202]:
                    xml_template = xml_template.replace("run_time", str(out_dict[pri_key]['fields']['run_time_sample']))
        if mca_id in [0x6001]:
            xml_template = xml_template.replace("build", str(out_dict["fpga_status"]["fields"]["build"]))
        
        with open(pathname, 'w+') as fout:
            fout.write(xml_template)
    