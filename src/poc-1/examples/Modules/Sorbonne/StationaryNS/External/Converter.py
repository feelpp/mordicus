#!/usr/bin/python3
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("input")
parser.add_argument("-o")
args = parser.parse_args()

input_name, input_extension = os.path.splitext(args.input)
if(args.o):
  output_name = args.o
else:
  output_name = input_name+"_new"+input_extension

# Read file and store data
infile = open(args.input, 'r') 
outfile = open(output_name, 'w') 
Lines = infile.readlines()

# first line is "NNodes NTri Nseg"
data = Lines[0].strip('\n').split(" ")
nnodes = int(data[0])
nelem = []
nelem_tot = 0
for d in data[1:len(data)]:
  nelem.append(int(d))
  nelem_tot += int(d)
print("Nnodes = " + str(nnodes) + "\nNelem  = "+str(nelem_tot))

# Header
outfile.write("$MeshFormat\n2.2 0 8\n$EndMeshFormat\n$Nodes\n");
# Points
cpt = 1 #line counter
outfile.write(str(nnodes)+"\n");
for i in range(nnodes): 
  outfile.write(str(i+1)+ " " + Lines[cpt]);
  cpt += 1
outfile.write("$EndNodes\n");
# Element
outfile.write("$Elements\n");
outfile.write(str(nelem_tot)+"\n");
for i in range(nelem_tot):
  #Loop on all element, without knowing what type they are
  elem = Lines[cpt].strip('\n').split(" ")
  if(len(elem)==3):
    # Segment
    outfile.write(str(i+1)+ " " ) # new element
    outfile.write("1 2 " + str(elem[2])+ " 0 " + str(elem[0]) +" "+str(elem[1])+"\n")
  elif(len(elem)==4):
    #Triangle
    outfile.write(str(i+1)+ " " ) # new element
    outfile.write("2 2 " + str(elem[3])+ " 0 " + str(elem[0]) +" "+str(elem[1])+" "+str(elem[2])+"\n")
  else:
    #Do not know
    print("Pas reconnu! ")
  cpt += 1
outfile.write("$EndElements\n");
# close everything
infile.close()
outfile.close()


