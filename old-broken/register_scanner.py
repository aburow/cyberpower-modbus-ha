from pyModbusTCP.client import ModbusClient
from xlwt import Workbook
import sys
import argparse
from tqdm import tqdm

#Function to write single Holding Register
def write_single_hold_register(ip_addr,port,valid_list,permission_list):
	write_confirm_list=[]
	write_confirm_data=[]
	client=ModbusClient(host=ip_addr,port=port,auto_open=True,auto_close=True,timeout=10)
	for i in tqdm(valid_list):
		data=client.write_single_register(i,43981) # HEX(ABCD) == int(43981)
		data=client.read_holding_registers(i,1)
		#print("Regiser: "+str(i)+" => Value: "+str(data))
		if data[0]:
			if 43981==data[0]:
				write_confirm_list.append(i)
				write_confirm_data.append(data[0])
				permission_list[i-1]="Read/Write"
	client.close()
	return write_confirm_list,write_confirm_data,permission_list

#Function to write single coil
def write_single_coil_register(ip_addr,port,coil_valid_list):
	write_coil_confirm_list=[]
	write_coil_confirm_data=[]
	client=ModbusClient(host=ip_addr,port=port,auto_open=True,auto_close=True,timeout=10)
	for i in coil_valid_list:
		data=client.write_single_register(i,43981) # HEX(ABCD) == int(43981)
		data=client.read_holding_registers(i,1)
		#print("Regiser: "+str(i)+" => Value: "+str(data))
		if data[0]:
			if 43981==data[0]:
				write_coil_confirm_list.append(i)
				write_coil_confirm_data.append(data[0])
	client.close()
	return write_coil_confirm_list,write_coil_confirm_data

#Function to read all the registers based on the parameter received
def read_valid_registers(ip_addr,port,reg):
	valid_list=[]
	data_list=[]
	permission_list=[]
	client=ModbusClient(host=ip_addr,port=port,auto_open=True,auto_close=True,timeout=10)
	for i in tqdm(range(1,500)):
		if reg == "hold":
			data=client.read_holding_registers(i,1)
		if reg == "input":
			data=client.read_input_registers(i,1)
		if reg == "discrete":
			data=client.read_discrete_inputs(i,1)
		if reg == "coil":
			data=client.read_coils(i,1)
		if data:
				valid_list.append(i)
				data_list.append(data[0])
				permission_list.append("Read")
	client.close()
	return valid_list,data_list,permission_list

	

#Write the result to Excel File
def write_to_excel(wb,register,valid_list,data_list,permission_list,reg_value):
	sheet=wb.add_sheet(register)
	sheet.write(0,0,"Register")
	sheet.write(0,1,"Permission")
	sheet.write(0,2,"Data")
	for i in range(len(valid_list)):
		sheet.write(i+1,0,valid_list[i]+reg_value)
		sheet.write(i+1,1,permission_list[i])
		sheet.write(i+1,2,data_list[i])
	wb.save("Modbus_Output.xls")
	return wb

#
def print_details(valid_list,data_list,operation):
	if valid_list:
		print("******************************")
		print(operation+" - Valid Registers: \n"+str(valid_list))
		print("******************************")
		print(operation+" - Valid Registers with Non-Zero Values")
		print("******************************")
		for i in range(len(valid_list)):
			if data_list[i]:
				print("Register :"+str(valid_list[i])+" => Value: "+str(data_list[i]))
		print("******************************")
	else:
		print("******************************")
		print("No Valid Register Found")
		print("******************************")

#Parse the input parameters
my_parser = argparse.ArgumentParser(description='Pass the input IP Address')
my_parser.add_argument('-i','--ipaddress', action='store', type=str,required=True, help='Input IP Address')
my_parser.add_argument('-p','--port', action='store', type=int,required=True, help='Port Number')
args = my_parser.parse_args()
ip_addr=args.ipaddress
port=args.port


#Create workbook to save the result
wb=Workbook()

#Read Input Registers - valid and Data [Read Only] - Up to 0x4F (79)
print("******************************")
print("Reading Input Registers - 0x04 (1-79)")
input_valid_list=[]
input_data_list=[]
input_permission_list=[]
client=ModbusClient(host=ip_addr,port=port,auto_open=True,auto_close=True,timeout=10)
for i in tqdm(range(1,80)):
	data=client.read_input_registers(i,1)
	if data:
		input_valid_list.append(i)
		input_data_list.append(data[0])
		input_permission_list.append("Read")
client.close()
wb=write_to_excel(wb,"Input_Register",input_valid_list,input_data_list,input_permission_list,30000)

#Holding Registers - valid and Data [Read and Write] - Up to 0x4F (79)
print("******************************")
print("Reading Holding Registers - 0x03 (1-79)")
hold_valid_list=[]
hold_data_list=[]
hold_permission_list=[]
client=ModbusClient(host=ip_addr,port=port,auto_open=True,auto_close=True,timeout=10)
for i in tqdm(range(1,80)):
	data=client.read_holding_registers(i,1)
	if data:
		hold_valid_list.append(i)
		hold_data_list.append(data[0])
		hold_permission_list.append("Read")
client.close()
if hold_data_list:
	print("Writing Holding Status - 0x06")
	write_hold_valid_list,write_hold_data_list,hold_permission_list=write_single_hold_register(ip_addr,port,hold_valid_list,hold_permission_list)
else:
	print("No valid Register Found to do Write Operation")
wb=write_to_excel(wb,"Holding_Register",hold_valid_list,hold_data_list,hold_permission_list,40000)

print("******************************")
print("Check the output Excel File - Modbus_Output.xls")
