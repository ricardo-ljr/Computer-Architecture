"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0  # program counter for stretch...
        # register is where you store what you retrieved from ram(memory)
        self.reg = [0] * 8
        self.ram = [0] * 256  # ram is memory

        self.branchtable = {}

        self.branchtable[HLT] = self.handle_hlt
        self.branchtable[LDI] = self.handle_ldi
        self.branchtable[PRN] = self.handle_prn
        self.branchtable[MUL] = self.handle_mul
        self.branchtable[PUSH] = self.handle_push
        self.branchtable[POP] = self.handle_pop
        self.branchtable[CALL] = self.handle_call
        self.branchtable[RET] = self.handle_ret
        self.branchtable[ADD] = self.handle_add

        self.SP = 7
        self.reg[self.SP] = 0xF4  # 244

    def ram_read(self, address):
        # Memory_Address_Register = MAR
        # MAR

        # takes address and returns the value at the address
        return self.ram[address]

    def ram_write(self, value, address):
        # Memory_Data_Register = MDR

        # takes an address and a value to write to it
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        # sets up a way to read the program being passed in by a user

        filename = sys.argv[1]
        print("\n\tFiles:", sys.argv)
        print("\tFilename:", filename, "\n")

        address = 0
        with open(filename) as f:
            for line in f:
                line = line.split("#")

                try:
                    value = int(line[0], 2)

                except ValueError:
                    continue

                self.ram[address] = value
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU (arithmetic logic unit) operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

#### Stack Handles Here ####

    def handle_push(self):
        # setup
        reg_index = self.ram_read(self.pc + 1)
        val = self.reg[reg_index]

        # decrement stack pointer
        self.reg[self.SP] -= 1

        top_of_stack = self.reg[self.SP]

        # insert val on to the stack
        self.ram_write(val, top_of_stack)

        self.pc += 2

    def handle_pop(self):

        reg_index = self.ram_read(self.pc + 1)

        top_of_stack = self.reg[self.SP]

        self.reg[reg_index] = self.ram_read(top_of_stack)

        # increment Stack Pointer
        self.reg[self.SP] += 1

        self.pc += 2
        #### IR here ####

    def handle_ldi(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)
        self.pc += 3

    def handle_hlt(self):
        self.pc += 1
        self.running = False
        return self.running

    def handle_prn(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def handle_mul(self):
        # Multiply the values in two registers together and store the result in registerA.
        reg_A = self.ram_read(self.pc + 1)
        reg_B = self.ram_read(self.pc + 2)

        self.alu("MUL", reg_A, reg_B)
        self.pc += 3

    def handle_call(self):

        self.reg[self.SP] -= 1

        self.ram[self.reg[self.SP]] = self.pc + 2

        reg_num = self.ram_read(self.pc+1)

        self.pc = self.reg[reg_num]

    def handle_ret(self):

        index = self.ram_read(self.pc + 1)

        self.reg[index] = self.ram_read(self.reg[self.SP])

        self.reg[self.SP] += 1

        self.pc = self.reg[index]

    def handle_add(self):
        reg1 = self.ram_read(self.pc + 1)
        reg2 = self.ram_read(self.pc + 2)

        self.alu("ADD", reg1, reg2)

        self.pc += 3

    def run(self):
        """Run the CPU."""
        # instrution register
        self.running = True
        while self.running:
            # grab the current instruction
            ir = self.ram_read(self.pc)
            # if we have an instruction that matches run it
            if ir in self.branchtable:
                self.branchtable[ir]()
            # if not print error
            else:
                print(f'Unknown instruction: {ir}, at address PC: {self.pc}')
                sys.exit(1)
