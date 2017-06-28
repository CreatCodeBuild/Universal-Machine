registers = [0, 0, 0, 0, 0, 0, 0, 0]
arrays = []
instruction_pointer = 0
print(registers)


def get_register(uint):
	A = (uint & 0b0000000111000000) >> 6
	B = (uint & 0b0000000000111000) >> 3
	C = (uint & 0b0000000000000111)

	return A, B, C

def program_info():
	print(registers)
	print('instruction pointer:', instruction_pointer)
	for a in arrays:
		if a == None or len(a) < 20:
			print(a)
		else:
			print(len(a))


if __name__ == '__main__':
	# load the initial program
	with open('codex.umz', mode='rb') as f:
		arrays.append(f.read())

	while instruction_pointer < len(arrays[0]):
		# print(instruction_pointer, arrays[0][4])

		uint = arrays[0][instruction_pointer*4:instruction_pointer*4+4]
		# print(uint, uint[0], uint[0] & 0b1111_0000)
		uint = int.from_bytes(uint, byteorder='big', signed=False)
		# print(bin(uint))
		operator = uint >> 28

		A, B, C = get_register(uint)
		# print(A, B, C, operator, instruction_pointer)
		# if operator != 0:
		# 	print(operator, '123')
		# 	exit()
		if operator == 0:
			# Conditional Move
			if registers[C] != 0:
				# The spec did say if register B should be written 0 afterwards
				registers[A] = registers[B]

		elif operator == 1:
			# Array Index
			try:
				registers[A] = arrays[registers[B]][registers[C]]
			except IndexError:
				exit()

		elif operator == 2:
			# Array Amendment
			try:
				arrays[registers[A]][registers[B]] = registers[C]
			except IndexError:
				exit()

		elif operator == 3:
			registers[A] = registers[B] + registers[C]

		elif operator == 4:
			registers[A] = registers[B] * registers[C]

		elif operator == 5:
			try:
				registers[A] = registers[B] / registers[C]
			except ZeroDivisionError:
				raise Exception('Divided By Zero')

		elif operator == 6:
			registers[A] = ~(registers[B] & registers[C])

		elif operator == 7:
			program_info()
			raise Exception('Halt')

		elif operator == 8:
			new_array = [0] * registers[C]
			try:
				pointer = arrays.index(None)
				arrays[pointer] = new_array
			except ValueError:
				pointer = len(arrays)
				arrays.append(new_array)
			registers[B] = pointer

		elif operator == 9:
			# Abandonment
			if registers[C] == 0 or arrays[registers[C]] == None:
				raise Exception('Try to abandon 0 array or an inactive array')
			try:
				arrays[registers[C]] = None
			except IndexError:
				raise Exception('Try to abandon unallocated array')

		elif operator == 10:
			value = registers[C]
			if 0 <= value <= 255:
				print(chr(value))
			else:
				raise Exception('Output value of out range')

		elif operator == 11:
			try:
				i = ord(input())
				if 0 <= i <= 255:
					registers[C] = i
				else:
					raise Exception('Input value of out range')
			except KeyboardInterrupt:
				registers[C] = 0xFFFF

		elif operator == 12:
			try:
				new_array = arrays[registers[B]][:]  # single all elements are integers, shallow copy is fine
			except IndexError and AttributeError:
				raise Exception('Try to copy inactive array or unallocated array')
			arrays[0] = new_array
			instruction_pointer = registers[C]

		elif operator == 13:
			A = (uint & 0b0000_1110_0000_0000_0000_0000_0000_0000) >> 25
			registers[A] = uint & 0b0000_0001_1111_1111_1111_1111_1111_1111

		else:
			raise Exception("Invalid Operator")

		instruction_pointer += 1
		# if instruction_pointer > 3:
		# 	exit()

