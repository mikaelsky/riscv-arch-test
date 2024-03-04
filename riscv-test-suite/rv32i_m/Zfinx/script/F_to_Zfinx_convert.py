#!/usr/bin/env python
# Python riscv-arch-test float to zfinx conversion

import os
import sys
import argparse

# Helper functions to convert F registers to X registers.
def safeRegReplaceR1(regLimit: int, r1: int, r2: int, r3: int) -> int:
    #check if r1 is overlappint system registers
    newReg = r1
    if (r1 <= regLimit):
        newReg = regLimit + 1 #set to smallest legal register
        for i in range(regLimit + 1,31):
            newReg = i
            if ((newReg != r2) & (newReg != r3)):
                break
    return newReg

def safeRegR4ReplaceR1(regLimit: int, r1: int, r2: int, r3: int, r4: int) -> int:
    #check if r1 is overlappint system registers
    newReg = r1
    if (r1 <= regLimit):
        newReg = regLimit + 1 #set to smallest legal register
        for i in range(regLimit + 1,31):
            newReg = i
            if ((newReg != r2) & (newReg != r3) & (newReg != r4)):
                break
    return newReg

# parse command line args
parser = argparse.ArgumentParser(description="Takes a riscv-test-arch F test suite file and outputs a Zfinx compliant test suite file as its output.")
parser.add_argument("test_file", help="Name of .S test file to convert")
parser.add_argument("-no_subnormal", action="store_true", help="Generates a test suite where subnormal numbers are filtered out")
parser.add_argument("--verbose", action="store_true", help="More verbose output")
args = parser.parse_args()

test_file = args.test_file
if (os.path.isfile(test_file)):
    sourceFile = open(args.test_file, 'r')
else:
    print("Test file: " + test_file + "not found.")
    exit(0)
 
for line in sourceFile:
    # set default number of parameters
    paramNum = 12
    # indicate hit
    replaceFunction = 0
    # convert FLEN to XLEN as we use XLEN to define FLEN size for Zfinx
    line = line.replace('FLEN', 'XLEN')
    # convert FLREG to LREG as zfinx doesn't have explicit float loads
    line = line.replace('FLREG', 'LREG')
    # convert FSREG to SREG as zfinx doesn't have explicit float stores
    line = line.replace('FSREG', 'SREG')
    # strip all white space
    line = line.strip()
    strippedLine = line.replace(' ','')
    # extract the function name
    parseLine = strippedLine.split('(')
    # do we match RVTEST_ISA?
    # RVTEST_ISA("RV32IF_Zicsr,RV32IFD_Zicsr,RV64IF_Zicsr,RV64IFD_Zicsr")
    # Replace FD with Zfinx and Zdinx
    if (parseLine[0] == 'RVTEST_ISA'):
        line = 'RVTEST_ISA("RV32IZfinx_Zicsr,RV32IZdinx_Zicsr,RV64IZfinx_Zicsr,RV64IZdinx_Zicsr,")'
    # do we match RVTEST_CASE?
    # RVTEST_CASE(0,"//check ISA:=regex(.*I.*F.*);def TEST_CASE_1=True;",fnmadd_b1)
    # replace the ISA test with Zfinx
    if (parseLine[0] == 'RVTEST_CASE'):
        # split over all parameters and append
        parseLine = parseLine + parseLine[2].split(',')
        # split the last paramter from end of line
        parseLine += parseLine[-1].split(')')
        # remove the interim strings
        parseLine.pop(2)
        parseLine.pop(-3)
        parseLine.pop(-1)

        line = parseLine[0] + "(" + parseLine[1] + "(" + '.*I.*Zfinx.*);def TEST_CASE_1=True"' + "," + parseLine[3] + ")"
        #line = "RVTEST_ISA(" + "'RVTEST_CASE(0,"+'"//check ISA:=regex(.*I.*Zfinx.*);def TEST_CASE_1=True;"' + parseLine[-1]

    # set the default Zfinx replacement register limit
    regLimit = 7
    # do we match the floating point register to register opertion?
    # TEST_FPSR_OP( inst, destreg, freg, rm, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg)
    if (parseLine[0] == 'TEST_FPSR_OP'):
        paramNum = 11+1
        replaceFunction = 1
    # TEST_FPSR_OP_NRM( inst, destreg, freg, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg)
    if (parseLine[0] == 'TEST_FPSR_OP_NRM'):
        paramNum = 10+1
        replaceFunction = 1
    # TEST_FPID_OP( inst, destreg, freg, rm, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg,load_instr)
    if (parseLine[0] == 'TEST_FPID_OP'):
        paramNum = 12+1
        replaceFunction = 1
    # TEST_FPIO_OP( inst, destreg, freg, rm, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg, load_instr)
    if (parseLine[0] == 'TEST_FPIO_OP'):
        paramNum = 12+1
        replaceFunction = 1
    # TEST_FPID_OP_NRM( inst, destreg, freg, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg)
    if (parseLine[0] == 'TEST_FPID_OP_NRM'):
        paramNum = 10+1
        replaceFunction = 1
    # TEST_FPIO_OP_NRM( inst, destreg, freg, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg, load_instr)
    if (parseLine[0] == 'TEST_FPIO_OP_NRM'):
        paramNum = 11+1
        replaceFunction = 1
    # TEST_FPRR_OP(inst, destreg, freg1, freg2, rm, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg)
    if (parseLine[0] == 'TEST_FPRR_OP'):
        paramNum = 12+1
        replaceFunction = 2
    # TEST_FPRR_OP_NRM(inst, destreg, freg1, freg2, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg) 
    if (parseLine[0] == 'TEST_FPRR_OP_NRM'):
        paramNum = 11+1
        replaceFunction = 2
    # TEST_FCMP_OP(inst, destreg, freg1, freg2, fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg)
    if (parseLine[0] == 'TEST_FCMP_OP'):
        paramNum = 11+1
        replaceFunction = 2
    # TEST_FPR4_OP(inst, destreg, freg1, freg2, freg3, rm , fcsr_val, correctval, valaddr_reg, val_offset, flagreg, swreg, testreg)
    if (parseLine[0] == 'TEST_FPR4_OP'):
        paramNum = 13+1
        replaceFunction = 3

    # Insert the X register field in the instruction call for test functions with 3 float parameters
    if (replaceFunction == 1):
        # split over all parameters and append
        parseLine = parseLine + parseLine[1].split(',')
        # split the last paramter from end of line
        parseLine += parseLine[-1].split(')')
        # remove the interim strings
        parseLine.pop(1)
        parseLine.pop(-3)
        # extract the test register values
        # is the destination register an integer register?
        if (parseLine[2].startswith('x')):
            destreg = int(parseLine[2].replace('x',''))
        if (parseLine[2].startswith('f')):
            destreg = int(parseLine[2].replace('f',''))
        # is the source register in integer register?
        if (parseLine[3].startswith('x')):
           reg1 = int(parseLine[3].replace('x',''))
        if (parseLine[3].startswith('f')):
           reg1 = int(parseLine[3].replace('f',''))
        # as zfinx is reusing X regs ensure we are not hitting the reserved x0-x4
        destreg = safeRegReplaceR1(regLimit, destreg, reg1, 0)
        reg1    = safeRegReplaceR1(regLimit, reg1, destreg, 0)
        # generate new function
        zfinx_function  = parseLine[0].replace("TEST", "TEST_ZFINX") + "(" + parseLine[1]
        # inject the new X register only parameters
        zfinx_function += ", x" + str(destreg) + ", x" + str(reg1)
        # fill in the remainder of the function parameters
        for i in range(4,paramNum):
            zfinx_function += ", " + parseLine[i]
        zfinx_function += ")"
        # Output original function line
        #print(line)
        line = zfinx_function
    if (replaceFunction == 2):
        # split over all parameters and append
        parseLine = parseLine + parseLine[1].split(',')
        # split the last paramter from end of line
        parseLine += parseLine[-1].split(')')
        # remove the interim strings
        parseLine.pop(1)
        parseLine.pop(-3)
        # extract the test register values
        if (parseLine[2].startswith('x')):
            destreg = int(parseLine[2].replace('x',''))
        if (parseLine[2].startswith('f')):
            destreg = int(parseLine[2].replace('f',''))
        reg1 = int(parseLine[3].replace('f',''))
        reg2 = int(parseLine[4].replace('f',''))
        # as zfinx is reusing X regs ensure we are not hitting the reserved x0-x4
        destreg = safeRegReplaceR1(regLimit, destreg, reg1, reg2)
        reg1    = safeRegReplaceR1(regLimit, reg1, destreg, reg2)
        reg2    = safeRegReplaceR1(regLimit, reg2, reg1, destreg)
        # generate new function
        zfinx_function  = parseLine[0].replace("TEST", "TEST_ZFINX") + "(" + parseLine[1]
        zfinx_function += ", x" + str(destreg) + ", x" + str(reg1) + ", x" + str(reg2)
        # fill in the remainder of the function parameters
        for i in range(5,paramNum):
            zfinx_function += ", " + parseLine[i]
        zfinx_function += ")"
        # Output original function line
        #print(line)
        line = zfinx_function
    if (replaceFunction == 3):
        # split over all parameters and append
        parseLine = parseLine + parseLine[1].split(',')
        # split the last paramter from end of line
        parseLine += parseLine[-1].split(')')
        # remove the interim strings
        parseLine.pop(1)
        parseLine.pop(-3)
        # extract the test register values
        destreg = int(parseLine[2].replace('f',''))
        reg1 = int(parseLine[3].replace('f',''))
        reg2 = int(parseLine[4].replace('f',''))
        reg3 = int(parseLine[5].replace('f',''))
        # as zfinx is reusing X regs ensure we are not hitting the reserved x0-x4
        destreg = safeRegR4ReplaceR1(regLimit, destreg, reg1, reg2, reg3)
        reg1    = safeRegR4ReplaceR1(regLimit, reg1, destreg, reg2, reg3)
        reg2    = safeRegR4ReplaceR1(regLimit, reg2, reg1, destreg, reg3)
        reg3    = safeRegR4ReplaceR1(regLimit, reg3, reg1, reg2, destreg)
        # generate new function
        zfinx_function  = parseLine[0].replace("TEST", "TEST_ZFINX") + "(" + parseLine[1]
        zfinx_function += ", x" + str(destreg) + ", x" + str(reg1) + ", x" + str(reg2) + ", x" + str(reg3)
        # fill in the remainder of the function parameters
        for i in range(6,paramNum):
            zfinx_function += ", " + parseLine[i]
        zfinx_function += ")\n"
        # Output original function line
        #print(line)
        line = zfinx_function


    print(line)

sourceFile.close()
