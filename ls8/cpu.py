import sys

# gtf > flag, ltf < flag, etf == flag
# FL bits: 00000LGE
ltf = 0b00000100  #less than flag
gtf = 0b00000010   #greater than flag
etf = 0b00000001   #equal to flag

print(f'etf: {etf}, gtf: {gtf}, ltf: {ltf}')
class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU.
        
        Add list properties to the CPU class to hold 256 bytes of memory and 8 general-purpose registers.
        - CPU Instruction
        - CPU Register
        -  RAM
        - CPU Program Counter

        """
        self.pc = 0 # Program counter/current instructor
        self.ir = None #Instruction Register,part of a CPU's control unit that holds the currently running instruction
        
        self.ram = [0] * 256  # Init RAM - 1 8-bit byte can store 256 possible values (0 to 255 in decimal or 0 to FF in hex base16

        self.reg = [0]* 8 #preallocate our register with 8, R0 -> R7
        self.halted = False 
        self.instruction = { 
            #decimal conversion
            0b00000001: self.HLT, #1
            0b10000010: self.LDI,#130
            0b01000111: self.PRN, #71
            0b10100010: self.MUL, #162
            0b01000101: self.PUSH, #69
            0b01000110: self.POP, #70
            0b01010000: self.CALL,#80
            0b00010001: self.RET, #17
            0b10100111: self.CMP, #167
            0b10100000: self.ADD, #160
            0b01010100: self.JMP, #84
            0b01010101: self.JEQ, #85
            0b01010110: self.JNE #86
        }

        self.sp = 7 #stack pointer location in registers
        self.reg[self.sp] = 0xF4 #initialize stack pointer at sp (7) to 0xF4
        self.flags = 0b00000001 #adds equal flag to ls8

    def load(self, filename):
        """Load a program into memory."""
        #First method called from ls8
        address = 0

        try:
            with open(filename) as f:
                for line in f:
                    #ignore comments
                    comment_split = line.split("#")

                    #Strip whitespace
                    num = comment_split[0].strip()

                    #Ignore blank lines
                    if num == '':
                        continue 

                    
                    # val = eval(f"0b{num}")
                    val = int(num, 2) #base 2
                    print(f'num: {num}, val: {val}')
                    self.ram_write(address, val)

                    print(f"RAM has been written to ---> val: {val}, address: {address}")
        
                    address += 1

        except FileNotFoundError:
            print(f" {sys.argv[0]}: {filename}not found")
            sys.exit(2)

        f.close()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        #Arithmetic and Logic

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL": 
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            '''
            CMP registerA registerB
            An instruction handled by the ALU that compares two values in registers
            '''
            #If registerA is less than registerB, set the Less-than L flag to 1, otherwise set it to 0.
            if self.reg[reg_a] < self.reg[reg_b]:
                self.flags = ltf
            #If registerA is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flags = gtf
            #If they are equal, set the Equal E flag to 1, otherwise set it to 0.
            else:
                self.flags = etf
        else:
            raise Exception("Unsupported ALU operation")
    
    # MAR: Memory Address Register, holds the memory address we're reading or writing
    # MDR: Memory Data Register, holds the value to write or the value just read
    def ram_read(self, MAR):
        '''
        ram_read() should accept the address to read and return the value stored there.
        '''
        return self.ram[MAR]

    def ram_write(self, MAR, MDR):
        '''
        raw_write() should accept a value to write, and the address to write it to.
        '''
        self.ram[MAR] = MDR 

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc, #0
            #self.fl, #Flags
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def HLT(self):
        self.halted = True 
        self.pc +=1
        sys.exit(0)

    def PRN(self):
        reg = self.ram_read(self.pc + 1)
        print(self.reg[reg])
        self.pc += 2

    def MUL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("MUL", reg_a, reg_b )
        self.pc += 3 

    def ADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("ADD", reg_a, reg_b)
        self.pc += 3

    def CMP(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu("CMP", reg_a, reg_b)
        self.pc+=3


    def LDI(self): 
        '''
        Set the value of a register to an integer
        Takes 3 args 1) immediate 2) register number 3) 8 bit immediate value 
        '''
        reg = self.ram_read(self.pc + 1)
        num = self.ram_read(self.pc + 2)
        #write to register
        self.reg[reg] = num
        self.pc += 3  

    def PUSH(self, MDR=None):
        '''
        PUSH register-
        Pushes the value in the given register on the stack - arg: MDR (memory data register)
        '''
        #Decrement SP by 1
        self.reg[self.sp] -= 1 

        #Get register arg from push
        data = MDR if MDR else self.reg[self.ram_read(self.pc + 1)]
        
        #Copy the value in the given register to the address pointed at by SP 
    
        self.ram_write(self.reg[self.sp], data)
        #Increment program counter by 2
        self.pc +=2
      
    def POP(self):
        '''
        POP register -
        Pops the value at the top of the stack into the given register
        '''
        #Get register arg from push 
        reg_a = self.ram_read(self.pc + 1)

        #Copy the value from the address pointed to by SP to the given register
        val = self.ram_read(self.reg[self.sp])

        #Copy the value - i.e. at register, add the value
        self.reg[reg_a] = val 
        #Increment SP
        self.reg[self.sp] +=1
        #Increment program counter by 2
        self.pc += 2
    
    def CALL(self):
        '''
        CALL register- Calls a subroutine (function) at the address stored in the register.
        1. The address of the instruction directly after CALL is pushed onto the stack. This allows us to return to where we left off when the subroutine finishes executing.
        2. The PC is set to the address stored in the given register. We jump to that location in RAM and execute the first instruction in the subroutine. The PC can move forward or backwards from its current location.
        '''
        self.PUSH(self.pc+2)
        self.pc = self.reg[self.ram_read(self.pc-1)]

    def RET(self):
        '''
        RET- Return from subroutine.
        Pop the value from the top of the stack and store it in the PC.

        '''

        self.pc = self.ram_read(self.reg[self.sp])
        self.reg[self.sp] += 1

    def JMP(self):
        '''
        JMP register
        Jump to the address stored in the given register.
        Set the PC to the address stored in the given register.
        '''
        #get the reg
        reg_a = self.ram_read(self.pc + 1)
        #Jump there
        self.pc = self.reg[reg_a]


    def JEQ(self):
        '''
        JEQ register
        if equal flag is set (true), jump to the address stored in the given register.
        '''
        #get the reg
        reg_a = self.ram_read(self.pc + 1)
        #Check if the equal flag is set to true 
        print(f"flags: {self.flags}, sp: {self.sp}")
        if self.flags == etf:
            #If so, jump to that address
            self.pc = self.reg[reg_a]

        #If,  not increment
        else:
            self.pc +=2
    
    def JNE(self):
        '''
        JNE register
        If E flag is clear (false, 0), jump to the address stored in the given register.
        '''
        #get the reg
        reg_a = self.ram_read(self.pc + 1)

        if self.flags != etf: 
            self.pc = self.reg[reg_a]
        else: 
            self.pc +=2


    def run(self):
        """Run the CPU."""

        # LDI - load 'immediate', store a value in a register or 'set this register this value' 
        # PRN - a psuedo-instruction that prints the nuemric value stored in a register
        # HLT - halt the CPU and exit the emulator

        #Flag that says if our program is running or not
        running = True 

        # a = self.ram_read(self.pc + 1)
        # b = self.ram_read(self.pc + 2)

        #While not halted..
        while not self.halted:
            #Get the instruction from ram and store in the local instructor register
            instruction = self.ram[self.pc]
            self.instruction[instruction]()
        
            # If instruction is HLT handle
            # if instruction == HLT or instruction == LDI or instruction == PRN or instruction == MUL or instruction == PUSH or instruction == POP: 
            #     self.instruction[instruction]()
            # else:
            #     raise Exception(f"Error: Instruction {instruction} does not exist")
            #     sys.exit(1)

            
