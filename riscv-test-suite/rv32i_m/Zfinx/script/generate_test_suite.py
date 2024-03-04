#!/usr/bin/env python
# Python riscv-arch-test float to zfinx conversion

import os
import sys
import argparse

# parse command line args
parser = argparse.ArgumentParser(description="Converts the F test suite to the Zfinx test suite. Must be called from the Zfinx test suite directory.\nDefault behavior is to convert all Zfinx compliant the F tests.")
parser.add_argument("F_test_suite_path", help="Path to the F test suite directory")
parser.add_argument("Zfinx_test_suite_path", help="Path to the Zfinx test suite directory")
parser.add_argument("-gcc_no_fdiv", action="store_true", help="Generates a GCC -no-fdiv compliant test suite. This will remove FDIV and FSQRT from the test suite")
parser.add_argument("-no_fused_mac", action="store_true", help="Generates a test suite without any fused MAC tests: FMADD, FMSUB, FNMADD, FNMSUB")
parser.add_argument("-no_fdiv", action="store_true", help="Generates a test suite without any division tests: FDIV")
parser.add_argument("-no_fsqrt", action="store_true", help="Generates a test suite without any square root tests: FSQRT")
parser.add_argument("-no_subnormal", action="store_true", help="Generates a test suite where subnormal numbers are filtered out")
parser.add_argument("--verbose", action="store_true", help="More verbose output")
args = parser.parse_args()

# Lists of float tests
# Unsupported F instruction with Zfinx
unsupportFloatTests = ["flw-align-01.S", "fsw-align-01.S", "fmv.w.x_b25-01.S","fmv.w.x_b26-01.S","fmv.x.w_b1-01.S ","fmv.x.w_b22-01.S","fmv.x.w_b23-01.S","fmv.x.w_b24-01.S","fmv.x.w_b27-01.S","fmv.x.w_b28-01.S","fmv.x.w_b29-01.S"]

floatAddTests       = ["fadd_b10-01.S","fadd_b1-01.S","fadd_b11-01.S","fadd_b12-01.S","fadd_b13-01.S","fadd_b2-01.S","fadd_b3-01.S","fadd_b4-01.S","fadd_b5-01.S","fadd_b7-01.S","fadd_b8-01.S"]
floatSubTests       = ["fsub_b10-01.S","fsub_b1-01.S","fsub_b11-01.S","fsub_b12-01.S","fsub_b13-01.S","fsub_b2-01.S","fsub_b3-01.S","fsub_b4-01.S","fsub_b5-01.S","fsub_b7-01.S","fsub_b8-01.S"]
floatConvertTests   = ["fcvt.s.w_b25-01.S ","fcvt.s.w_b26-01.S ","fcvt.s.wu_b25-01.S","fcvt.s.wu_b26-01.S","fcvt.w.s_b1-01.S  ","fcvt.w.s_b22-01.S ","fcvt.w.s_b23-01.S ","fcvt.w.s_b24-01.S ","fcvt.w.s_b27-01.S ","fcvt.w.s_b28-01.S ","fcvt.w.s_b29-01.S ","fcvt.wu.s_b1-01.S ","fcvt.wu.s_b22-01.S","fcvt.wu.s_b23-01.S","fcvt.wu.s_b24-01.S","fcvt.wu.s_b27-01.S","fcvt.wu.s_b28-01.S","fcvt.wu.s_b29-01.S"]
floatMultTests      = ["fmul_b1-01.S","fmul_b2-01.S","fmul_b3-01.S","fmul_b4-01.S","fmul_b5-01.S","fmul_b6-01.S","fmul_b7-01.S","fmul_b8-01.S","fmul_b9-01.S"]
floatDivTests       = ["fdiv_b1-01.S","fdiv_b20-01.S","fdiv_b2-01.S","fdiv_b21-01.S","fdiv_b3-01.S","fdiv_b4-01.S","fdiv_b5-01.S","fdiv_b6-01.S","fdiv_b7-01.S","fdiv_b8-01.S","fdiv_b9-01.S"]
floatSystemTests    = ["fclass_b1-01.S"]
floatCompareTests   = ["feq_b1-01.S","feq_b19-01.S","fle_b1-01.S","fle_b19-01.S","flt_b1-01.S","flt_b19-01.S"]
floatFusedMACTests  = ["fmadd_b1-01.S","fmadd_b14-01.S","fmadd_b15-01.S","fmadd_b16-01.S","fmadd_b17-01.S","fmadd_b18-01.S","fmadd_b2-01.S","fmadd_b3-01.S","fmadd_b4-01.S","fmadd_b5-01.S","fmadd_b6-01.S","fmadd_b7-01.S","fmadd_b8-01.S"]
floatMinMaxTests    = ["fmax_b1-01.S","fmax_b19-01.S","fmin_b1-01.S","fmin_b19-01.S"]
floatFusedMSCTest   = ["fmsub_b1-01.S","fmsub_b14-01.S","fmsub_b15-01.S","fmsub_b16-01.S","fmsub_b17-01.S","fmsub_b18-01.S","fmsub_b2-01.S","fmsub_b3-01.S","fmsub_b4-01.S","fmsub_b5-01.S","fmsub_b6-01.S","fmsub_b7-01.S","fmsub_b8-01.S"]
floatFusednMACTests = ["fnmadd_b1-01.S","fnmadd_b14-01.S","fnmadd_b15-01.S","fnmadd_b16-01.S","fnmadd_b17-01.S","fnmadd_b18-01.S","fnmadd_b2-01.S","fnmadd_b3-01.S","fnmadd_b4-01.S","fnmadd_b5-01.S","fnmadd_b6-01.S","fnmadd_b7-01.S","fnmadd_b8-01.S"]
floatFusednMSCTests = ["fnmsub_b1-01.S","fnmsub_b14-01.S","fnmsub_b15-01.S","fnmsub_b16-01.S","fnmsub_b17-01.S","fnmsub_b18-01.S","fnmsub_b2-01.S","fnmsub_b3-01.S","fnmsub_b4-01.S","fnmsub_b5-01.S","fnmsub_b6-01.S","fnmsub_b7-01.S","fnmsub_b8-01.S"]
floatSignTests      = ["fsgnj_b1-01.S","fsgnjn_b1-01.S","fsgnjx_b1-01.S"]
floatSQRTTests      = ["fsqrt_b1-01.S""fsqrt_b20-01.S","fsqrt_b2-01.S","fsqrt_b3-01.S","fsqrt_b4-01.S","fsqrt_b5-01.S","fsqrt_b7-01.S","fsqrt_b8-01.S","fsqrt_b9-01.S"]

# Setup basic Zfinx test suite
if (args.verbose):
    print("Generating the basic test suite with FADD, FSUB, FCVT.S.W/WU, FCVT.W/WU.S, FMUL, FCLASS, FEQ/LE/LT, FMIN/MAX, FSGNJ")
zfinxTestList = floatAddTests + floatSubTests + floatConvertTests + floatMultTests + floatSystemTests + floatCompareTests + floatMinMaxTests + floatSignTests;

# Are we adding fdiv tests?
if ((args.gcc_no_fdiv) or (args.no_fdiv)):
    if (args.verbose):
        print("Adding FDIV tests to the test suite")
    zfinxTestList += floatDivTests

if ((args.gcc_no_fdiv) or (args.no_fsqrt)):
    if (args.verbose):
        print("Adding FSQRT tests to the test suite")
    zfinxTestList += floatSQRTTests

if (args.no_fused_mac):
    if (args.verbose):
        print("Adding FMADD, FMSUB, FNMADD, FNMSUB tests to the test suite")
    zfinxTestList += floatFusedMACTests + floatFusedMSCTest + floatFusednMACTests + floatFusednMSCTests

if (args.no_subnormal):
    if (args.verbose):
        print("Calling the conversion function with no subnormals")

for test in zfinxTestList:
    if (args.no_subnormal):
        cmd = args.Zfinx_test_suite_path + "script/F_to_Zfinx_convert.py " + args.F_test_suite_path + "src/" + test + " > " + args.Zfinx_test_suite_path + "src/" + test
    else:
        cmd = args.Zfinx_test_suite_path + "script/F_to_Zfinx_convert.py " + args.F_test_suite_path + "src/" + test + " > " + args.Zfinx_test_suite_path + "src/" + test
    if (args.verbose):
        print("Converting test: " + test)
        print("Converstion command: " + cmd)
    os.system(cmd)
