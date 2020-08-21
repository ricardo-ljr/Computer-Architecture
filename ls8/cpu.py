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
CMP = 0b10100111
JEQ = 0b01010101
JNE = 0b01010110
JMP = 0b01010100
AND = 0b10101000
NOT = 0b01101001
OR = 0b10101010
MOD = 0b10100100
XOR = 0b10101011
SHL = 0b10101100
SHR = 0b10101101


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
        self.branchtable[CMP] = self.handle_cmp
        self.branchtable[JEQ] = self.handle_jeq
        self.branchtable[JNE] = self.handle_jne
        self.branchtable[JMP] = self.handle_jmp
        self.branchtable[AND] = self.handle_and
        self.branchtable[NOT] = self.handle_not
        self.branchtable[OR] = self.handle_or
        self.branchtable[MOD] = self.handle_mod
        # self.branchtable[SHL] = self.handle_shl
        self.branchtable[XOR] = self.handle_xor

        self.SP = 7
        self.reg[self.SP] = 0xF4  # 244

        # Flag here
        self.fl = 0b00000000

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
        elif op == "CMP":
            # Flags register
            if self.reg[reg_a] < self.reg[reg_b]:
                # 100
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                # 010
                self.fl = 0b00000010
            elif self.reg[reg_a] == self.reg[reg_b]:
                # 001
                self.fl = 0b00000001
            else:
                # 000
                self.fl = 0b00000000
        elif op == "AND":
            for i in range(len(self.reg[reg_a]) - 1):
                self.reg[reg_a][i] = self.reg[reg_a][i] * self.reg[reg_b][i]
        elif op == "NOT":
            for each in self.reg[reg_a]:
                if each == 0:
                    each = 1
                else:
                    each = 0
        elif op == "OR":
            for i in range(len(self.reg[reg_a]) - 1):
                if self.reg[reg_a][i] and self.reg[reg_b][i] == 0:
                    self.reg[reg_a][i] = 0
                else:
                    self.reg[reg_a][i] = 1
        elif op == "XOR":
            for i in range(len(self.reg[reg_a]) - 1):
                if self.reg[reg_a][i] == self.reg[reg_b][i]:
                    self.reg[reg_a][i] = 0
                else:
                    self.reg[reg_a][i] = 1
        elif op == "SHL":
            self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >> self.reg[reg_b]
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

        # index = self.ram_read(self.pc + 1)

        # self.reg[index] = self.ram_read(self.reg[self.SP])

        # self.reg[self.SP] += 1

        # self.pc = self.reg[index]

        self.pc = self.ram[self.reg[self.SP]]
        self.reg[self.SP] += 1

    def handle_add(self):
        reg1 = self.ram_read(self.pc + 1)
        reg2 = self.ram_read(self.pc + 2)

        self.alu("ADD", reg1, reg2)

        self.pc += 3

#### Sprint Challenge ####

    def handle_cmp(self):
        reg1 = self.ram_read(self.pc + 1)
        reg2 = self.ram_read(self.pc + 2)

        self.alu("CMP", reg1, reg2)
        self.pc += 3

    def handle_jeq(self):
        if self.fl == 0b00000001:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2

    def handle_jmp(self):
        self.pc = self.ram_read(self.pc + 1)

    def handle_jne(self):
        if self.fl != 0b00000001:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2

    def handle_mod(self):
        reg1 = self.reg[self.ram_read(self.pc + 1)]
        reg2 = self.reg[self.ram_read(self.pc + 2)]

        try:
            self.reg[self.ram_read(self.pc + 1)] = (reg1 % reg2)

        except ZeroDivisionError:

            sys.exit()

#### Stretch Sprint Challenge ####

    def handle_and(self):
        reg_1 = self.ram_read(self.pc + 1)
        reg_2 = self.ram_read(self.pc + 2)

        self.alu("AND", reg_1, reg_2)
        self.pc += 3

    def handle_not(self):
        reg_1 = self.ram_read(self.pc + 1)
        reg_2 = self.ram_read(self.pc + 2)

        self.alu("NOT", reg_1, reg_2)
        self.pc += 2

    def handle_or(self):
        reg_1 = self.ram_read(self.pc + 1)
        reg_2 = self.ram_read(self.pc + 2)

        self.alu("OR", reg_1, reg_2)
        self.pc += 3

    def handle_xor(self):
        reg_1 = self.ram_read(self.pc + 1)
        reg_2 = self.ram_read(self.pc + 2)

        self.alu("XOR", reg_1, reg_2)
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
