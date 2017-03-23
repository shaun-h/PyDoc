#!/usr/bin/env python3

# Copyright (c) 2016 Lukas Kollmer<lukas@kollmer.me>
#https://gist.github.com/lukaskollmer/a09c0278d2d224b9f4839a895ebb9988

from ctypes import *
from objc_util import ObjCClass

class c_vm_statistics(Structure):
	_fields_ = [('free_count', c_uint),
								('active_count', c_uint),
								('inactive_count', c_uint),
								('wire_count', c_uint),
								('zero_fill_count', c_uint),
								('reactivations', c_uint),
								('pageins', c_uint),
								('pageouts', c_uint),
								('faults', c_uint),
								('cow_faults', c_uint),
								('lookups', c_uint),
								('hits', c_uint),
								('purgeable_count', c_uint),
								('purges', c_uint),
								('speculative_count', c_uint)]

def get_memory_details():
	NSProcessInfo = ObjCClass('NSProcessInfo')
	NSByteCountFormatter = ObjCClass('NSByteCountFormatter')



	c = cdll.LoadLibrary(None)

	mach_host_self = c.mach_host_self
	mach_host_self.restype = c_uint
	mach_host_self.argtypes = [c_void_p]

	host_page_size = c.host_page_size
	host_page_size.restype = c_int
	host_page_size.argtypes = [c_uint, POINTER(c_uint)]

	host_statistics = c.host_statistics
	host_statistics.restype = c_int
	host_statistics.argtypes = [c_uint, c_int, POINTER(c_int), POINTER(c_uint)]


	host_port = c_uint()
	host_size = c_uint()
	page_size = c_uint()


	host_port = mach_host_self(None)
	host_size = c_uint(int(sizeof(c_vm_statistics) / sizeof(c_int)))
	host_page_size(host_port, byref(page_size))



	vm_stat = c_vm_statistics()

	HOST_VM_INFO = c_int(2) # This is a c macro
	KERN_SUCCESS = 0 # Another c macro (No c_int initializer used because we don't pass it to a c function)

	get_host_statistics = host_statistics(host_port, HOST_VM_INFO, cast(byref(vm_stat), POINTER(c_int)), byref(host_size))

	if not get_host_statistics == int(KERN_SUCCESS):
		print("Failed to fetch vm statistics")
		return None


	mem_used = (vm_stat.active_count + vm_stat.inactive_count + vm_stat.wire_count) * int(page_size.value)
	mem_free = vm_stat.free_count * int(page_size.value)
	mem_total = mem_used + mem_free

	physical_memory = NSProcessInfo.processInfo().physicalMemory()

	byteCountFormtter = NSByteCountFormatter.new()
	mem_used = byteCountFormtter.stringFromByteCount_(mem_used)
	mem_free = byteCountFormtter.stringFromByteCount_(mem_free)
	mem_total = byteCountFormtter.stringFromByteCount_(mem_total)
	physical_memory = byteCountFormtter.stringFromByteCount_(physical_memory)
	
	return {'used': mem_used, 'free': mem_free, 'total': mem_total, 'physical':physical_memory}

if '__main__' == __name__:
	data = get_memory_details()
	print('used:  ', data['used'])
	print('free:  ', data['free'])
	print('total: ', data['total'])
	print('total (according to Cocoa): ', data['physical'])
