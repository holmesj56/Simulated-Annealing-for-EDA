import re
import random
import time
import argparse  
from tqdm import tqdm
from pathlib import Path
import math 
pbar = tqdm(total=100)
progress = 0
import matplotlib.pyplot as plt
class Block:
    def __init__(self,block_name,is_soft,length,width,area,min_asp,max_asp):
        self.block_name = block_name
        
        self.is_soft = is_soft # True for a soft-macro, None (or False) for a hard-macro
        self.length = length
        self.width = width
        self.area = area
        # To keep track of slicing tree for incremental cost update
        self.parent_block = None
        self.left_child = None
        self.right_child = None
        self.elements=[block_name]
        # For soft-macros only, otherwise None
        self.min_aspect_ratio =min_asp   # width will be 0.3 l ength , and length , 
        self.max_aspect_ratio = max_asp     # width willl be 3  legthh 1 
        self.optimal_aspect_ratio = 1 # the optimal aspect ratio
        # To print the coordinates of each block.
        self.x_coordinate = 0.0 # lower left
        self.y_coordinate = 0.0 # lower left
        self.xt_coordinate=0.0
        self.yt_coordinate=0.0
class Stack:            #creating stack
    def __init__(self):
        self.items = [] 

    def is_empty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
       
        if self.is_empty():
            raise IndexError(" empty stack")
        return self.items.pop()

    def peek(self):
        if self.is_empty():
            raise IndexError(" empty stack")
        return self.items[-1]

    def size(self):
        return len(self.items)
def read(file,texthead):            #taking data from the block files 
    with open(file,'r') as f:
        for line in f:
            if line.strip().startswith(texthead):                    

                number=line.split(':')[1].strip()    #taking the second element in the line 
                return int(number.strip())
def file_in(path):
    file_path = Path(path)
    if not file_path.is_file():
        raise argparse.ArgumentTypeError("The file not found")
    return file_path
def parse_args():
    """Parse command  arguments"""
    parser = argparse.ArgumentParser(description="Floorplan optimization")
    parser.add_argument('--input', type=file_in, required=True)
    parser.add_argument('--output', type=str, required=True)
    return parser.parse_args()
def file_in(path):
    """Verify file path"""
    file_path = Path(path)
    if not file_path.is_file():
        raise argparse.ArgumentTypeError("The file not found")
    return file_path
def main():
    hard_blocks={}
    soft_blocks={}
    args = parse_args()
    file_path = args.input
    out_path = args.output
    hard_blocks,soft_blocks,softnumber,hardnumber=create_classes(file_path,hard_blocks,soft_blocks)  #creating classes with hardblocks and softblocks 
    polish=[]    # list to store random polish expression 
    if  len(list(hard_blocks.keys()))!=0:
        ordered_block_names = list(hard_blocks.keys())              # getting the hard_block keys
    else:
        ordered_block_names=list(soft_blocks.keys())            #getting the softblock keys 
    if len(soft_blocks)!=0:
        hard_blocks=soft_blocks
    polish.append(ordered_block_names[0])                           
    polish.append(ordered_block_names[1])
    polish.append('|')                                     # creating sample polish expression 

    for i, block in enumerate(ordered_block_names[2:], start=2):
        polish.append(hard_blocks[block].block_name)  # Access the property or method correctly
        if i % 2 == 0:
            polish.append('-')
        else:
            polish.append('|')
    jsj=0
    j=area(polish,hard_blocks)
    sol=simulated_annealing(polish,hard_blocks,soft_blocks)           #calling solution from simulated annealing .    
    Black_area=0
    Black_area,white_area=entire_area(sol,area(sol,hard_blocks),hard_blocks)
    coordinate(sol,hard_blocks)
    with open(out_path,'w') as file:                                    #creating a out file.
        file.write(f"Final area = {area(sol,hard_blocks)}\n")
        file.write(f"Black area ={Black_area} \n\n")
        file.write("Block_name lower_left(x,y)coordinate upper_right(x,y)coordinate\n")
        for bloc_key, bloc in enumerate(polish):
            if bloc not in ['|','-']:                    #writing in coordinates of each blocks . it is obtained from the dictionary hard_blocks which is a dictionary of classes.
                block_info = f"{hard_blocks[bloc].block_name}({hard_blocks[bloc].x_coordinate :.6f},{hard_blocks[bloc].y_coordinate:.6f}) ({((hard_blocks[bloc].x_coordinate) + (hard_blocks[bloc].width)):.6f},{((hard_blocks[bloc].y_coordinate) + (hard_blocks[bloc].length)):.6f})"
                file.write(block_info + "\n")
def extract(line):                       #extract the hardrectilinear blocks and soft rectangular block from the block file.
    
    name_match = re.match(r"(\w+)\s", line)
    if name_match:
        name = name_match.group(1)
    else:
        name = None
    coordinates = re.findall(r"\((\d+),\s*(\d+)\)", line)  #taking the initial coordinates for length and width
    if len(coordinates) >= 3:
        width = int(coordinates[2][0])                   
        height = int(coordinates[2][1])
    else:
        width = None
        height = None
    return Block(name,False , height,width,height*width,0,0)
def soft_extract(line):
    # Define the pattern using regular expression
    pattern = r'(sb\d+)\s+softrectangular\s+(\d+)\s+([\d.]+)\s+([\d.]+)'
    parts =line.split()
    area=int(parts[2])
    min_aspect_ratio = float(parts[3])
    max_aspect_ratio = float(parts[4])
    # Match the pattern
    match = re.match(pattern, line)

    # Extract the values
    if match:
        
        sb = match.group(1)
        num = random.randint(1, 2)
        value_after_softrectangular = int(match.group(2))

        if num==1:
            width=math.sqrt(value_after_softrectangular*0.3)
            length=math.sqrt(value_after_softrectangular/0.3)
        else:
            width=math.sqrt(value_after_softrectangular*3)
            length=math.sqrt(value_after_softrectangular/3)
            
               # return the elements as a class object .
        return Block(sb,True,length,width,value_after_softrectangular,min_aspect_ratio,max_aspect_ratio)
    else:
        return None, None

def create_classes(file_path,hard_blocks,soft_blocks):         # create class based on Hard and Soft blocks 
    softnumber=read(file_path,'NumSoftRectangularBlocks')     #checking if SoftRectangular is in the line   
    hardnumber=read(file_path,'NumHardRectilinearBlocks')     # checking if hardrectilinear is in the line 

    
    with open(file_path,'r') as f:
        for line in f:
            if softnumber!=0 or  hardnumber!=0:                           # checking if the number of hardblocks and softblocks 
                if line.startswith('sb'):
                    
                    if 'hard' in line:
                        block=extract(line)
                        hardnumber=hardnumber-1
                        hard_blocks[block.block_name] = block
                    if 'soft' in line:
                        block=soft_extract(line)
                        softnumber=softnumber-1
                        soft_blocks[block.block_name] = block
        return hard_blocks,soft_blocks,softnumber,hardnumber
def area(polish,hard_blocks):                    #area function cacluation .

    k=1
    blc1={}
    polish_mod=[]
    stack=Stack()
    stack = Stack()
    
    for pol in polish:
        if pol == '|':
            if stack.size() < 2:
                print("Error: Not enough elements in the stack for operation '|'.")
                return
            a = stack.pop()     #using a  stack to pop elements when an operation is seen
            b = stack.pop()

            if a not in hard_blocks or b not in hard_blocks: 
                print(f"Error: Block '{a}' or '{b}' not found.")
                return 
            x = hard_blocks[a].width + hard_blocks[b].width
            y = max(hard_blocks[a].length, hard_blocks[b].length)
            
            # Temp stored in hard_blocks  (hardblocks is a dictionary . Temporary Class objects created)
            hard_blocks[f"temp{k}"] = Block(f"temp{k}", False, y, x,y*x,0,0)
        
            stack.push(f"temp{k}")
            k+=1
        elif pol == '-':
            if stack.size() < 2:
                print("Error: Not enough elements in the stack for operation '-'.")
                return
            a = stack.pop()
            b = stack.pop()

            if a not in hard_blocks or b not in hard_blocks:
                print(f"Error: Block '{a}' or '{b}' not found.")
                return
            
            x = max(hard_blocks[a].width, hard_blocks[b].width)
            y = hard_blocks[a].length + hard_blocks[b].length
            # Temp stored in hardblocks
            hard_blocks[f"temp{k}"] = Block(f"temp{k}", False, y, x,y*x,0,0)
         
            stack.push(f"temp{k}")
            k+=1                                                    
        else:
            if pol not in hard_blocks:
                print(f"Error: Block '{pol}' not found.")
                return
            stack.push(pol)
    
    return hard_blocks[f"temp{k-1}"].area
def coordinate(polish,hard_blocks):
    k=1
    stack = Stack()
    print(polish)
    for pol in polish:
        if pol == '|':
            if stack.size() < 2:
                print("Error: Not enough elements in the stack for operation '|'.")
                return
            a = stack.pop()     
            b = stack.pop()

            if a not in hard_blocks or b not in hard_blocks: 
                print(f"Error: Block '{a}' or '{b}' not found.")
                return 
            x = hard_blocks[a].width + hard_blocks[b].width
            y = max(hard_blocks[a].length, hard_blocks[b].length)
            
            # Temporarily store this new block in hard_blocks
            hard_blocks[f"temp{k}"] = Block(f"temp{k}", False, y, x,y*x,0,0)
            hard_blocks[f"temp{k}"].elements=hard_blocks[a].elements+hard_blocks[b].elements
            for elements in hard_blocks[a].elements:
                hard_blocks[elements].x_coordinate= hard_blocks[elements].x_coordinate+ hard_blocks[b].width
            stack.push(f"temp{k}")
            k+=1
        elif pol == '-':
            if stack.size() < 2:
                print("Error: Not enough elements in the stack for operation '-'.")
                return
            a = stack.pop()
            b = stack.pop()

            if a not in hard_blocks or b not in hard_blocks:
                print(f"Error: Block '{a}' or '{b}' not found.")
                return
            
            x = max(hard_blocks[a].width, hard_blocks[b].width)
            y = hard_blocks[a].length + hard_blocks[b].length
            # Temporarily store temp in hard_blocks
            hard_blocks[f"temp{k}"] = Block(f"temp{k}", False, y, x,y*x,0,0)
            hard_blocks[f"temp{k}"].elements=hard_blocks[a].elements+hard_blocks[b].elements
            for elements in hard_blocks[b].elements:
                hard_blocks[elements].y_coordinate= hard_blocks[elements].y_coordinate+ hard_blocks[a].length
            stack.push(f"temp{k}")
            k+=1                                                    
        else:
            if pol not in hard_blocks:
                print(f"Error: Block '{pol}' not found.")
                return
            stack.push(pol)
    return hard_blocks[f"temp{k-1}"].area


def perturb(solut,hard_blocks,soft_blocks): #perturbation   
    global possible_random_moves
    sol=solut.copy()

    if soft_blocks:           #no rotaion for softblocks and aspect ratio adjustment  for soft blocks 
        num=[1,2,3,5]
    else:
        num=[1,2,3,4]          #no aspect ratio change for hardblocks      
    random_num = random.choice(num)     # selecting a random number 
    
    if random_num == 1:         # operation one exchange operands
        width_length=0
        module=1
        my_list = []
        for i in range(len(sol)):           
            if sol[i] not in ['|', '-']: 
                my_list.append(i)          # creating a list were indices is the polish indices without operations 
        s = len(my_list) - 1
        random_ind = random.choice(range(len(my_list) - 2))  
        t = sol[my_list[random_ind]]                                       # randomly choose an index and exchange with the next element in the list .
        sol[my_list[random_ind]] = sol[my_list[random_ind + 1]]  
        sol[my_list[random_ind + 1]] = t
        
    
    elif random_num == 2:         # compliment series of operators
        width_length=0
        module=1 
        my_list = [k for k, element in enumerate(sol) if element not in ['|', '-']]
        done=0
        while(done==0):
            random_ind1,random_ind2=sorted(random.sample(my_list,2))         # taking two indices randomly in ascending order 
            for i in range (random_ind1,random_ind2+1):
                if sol[i] in ['|','-']:
                    if sol[i] == '|':                               #complement operators  between them  .
                        sol[i] = '-'
                        done+=1
                    elif sol[i] == '-':
                        sol[i] = '|'
                        done+=1
        done=0
      
    
    elif random_num ==3:  
        width_length=0
        module=1        #  exchange operand and operator 
        sol=solut.copy()
        j=0
        jj=0
        while j==0:
            
            k=len(sol)
            n=random.randint(2, k - 2)            #randomly select a number and complement operator right after 
            s=0
            while(s==0):     
                jj+=1
                if sol[n] not in ['|','-'] and sol[n+1] in ['|','-'] :
                    if sol[n+1] in ['|', '-'] and sol[n-1] in ['|', '-']:
                        n=random.randint(2,k-2)
                    else:
                        temp=sol[n]
                        sol[n]=sol[n+1]
                        sol[n+1]=temp
                        s=1
                        
                elif sol[n] in ['|','-'] and sol[n+1] not in ['|','-']:
                    if sol[n+1] in ['|', '-'] and sol[n-1] in ['|', '-']:
                        n=random.randint(2,k-2)
                    else:
                        s=1
                        temp=sol[n]
                        sol[n]=sol[n+1]
                        sol[n+1]=temp
                else:
                    n=random.randint(2,k-2)
                try:
                    area(sol,hard_blocks)             # checking if the are passes without any errors looking for a normalized polish 
                    j=1
                
                except TypeError:
                    s=0
    elif random_num==4:
        my_list = [k for k, element in enumerate(solut) if element not in ['|', '-']] # for rotation , look for operands 
        ran=random.choice(my_list)
        temp=hard_blocks[solut[ ran]].width 
        hard_blocks[solut[ran]].width=hard_blocks[solut[ran]].length               #swaping the length and width of the operators .
        hard_blocks[solut[ran]].length=temp
        module=solut[ran]
        width_length=0
    else:
        my_list = [k for k, element in enumerate(solut) if element not in ['|', '-']]
        ran = random.choice(my_list)
        if (hard_blocks[solut[ran]].max_aspect_ratio == hard_blocks[solut[ran]].min_aspect_ratio):
            num=1
        else:
            num = random.choice([1, 2,3])               # for softblocks adjusting the aspect ratio.

        # Get the original dimensions and area
        module = hard_blocks[solut[ran]]
        original_width = module.width
        original_length = module.length
        original_area = original_width * original_length

        if num == 1:
            # Set aspect ratio to 0.3 (width/length)
            aspect_ratio = hard_blocks[solut[ran]].min_aspect_ratio
            module=hard_blocks[solut[ran]]
            
            new_width=math.sqrt(original_area*aspect_ratio)                # adjusting aspect ratios 
            hard_blocks[solut[ran]].width=new_width
            new_length= math.sqrt(original_area/aspect_ratio)
            hard_blocks[solut[ran]].length =new_length
            new_area=hard_blocks[solut[ran]].width*hard_blocks[solut[ran]].length
            hard_blocks[solut[ran]].area=new_area

        elif num == 2:
            # Set aspect ratio to 3 (width/length)
            aspect_ratio = hard_blocks[solut[ran]].min_aspect_ratio         #aspect ratio's obtained from the class.
            module=hard_blocks[solut[ran]]
            
            new_width=math.sqrt(original_area*aspect_ratio)
            hard_blocks[solut[ran]].width=new_width
            new_length= math.sqrt(original_area/aspect_ratio)
            hard_blocks[solut[ran]].length =new_length
            new_area=hard_blocks[solut[ran]].width*hard_blocks[solut[ran]].length
            hard_blocks[solut[ran]].area=new_area

        else:
            # Make the block square
            aspect_ratio=1
            module=hard_blocks[solut[ran]]
            
            new_width=math.sqrt(original_area*aspect_ratio)
            hard_blocks[solut[ran]].width=new_width
            new_length= math.sqrt(original_area/aspect_ratio)
            hard_blocks[solut[ran]].length =new_length
            new_area=hard_blocks[solut[ran]].width*hard_blocks[solut[ran]].length
            hard_blocks[solut[ran]].area=new_area
            

        # Storing original and new dimensions for any further use
        width_length = [original_width, original_length]
    return sol,random_num,module,width_length

def acceptMove(del_cost, T, random_num, block, width_length,hard_blocks):
    
    if del_cost < 0:
        return True
    else:
      
        boltz = math.exp(-del_cost / T)
        
        
        r = random.uniform(0, 1)
        if r < boltz:
            return True
        else:
            if random_num == 4:
               
                temp = hard_blocks[block].width                                       # if the rotation is not accepted change the swap
                hard_blocks[block].width = hard_blocks[block].length
                hard_blocks[block].length = temp
               
            elif random_num == 5:                           # if the aspect ratio is not accepted replace the original value.
                block.width = width_length[0]
                block.length = width_length[1]
               
            return False
def entire_area(solution,area_solu,hard_blocks):      # calcuate the white area and black areas 
    white_area=0
    for i ,pol in enumerate(solution):
        if pol in hard_blocks:
            white_area=white_area+hard_blocks[pol].area
    Black_area=area_solu-white_area
    return Black_area,white_area


def simulated_annealing(polish,hard_blocks,soft_blocks):
    currSolution = polish 
    nextSol = []        #array of next solutions 
    arealist = []       #array to store accepted area values
    block_size = math.ceil(len(polish)/2)

    if hard_blocks[polish[0]].is_soft==True:
        T = 36000         #initial T value
        T_freez = 0.01   
        num_moves = 6*block_size
        cooling_rate = 0.967
    else:
        T = 7000         #initial T value
        T_freez = 0.01
        num_moves = 3*block_size
        cooling_rate = 0.95

    iter = int(math.log(T_freez / T) / math.log(cooling_rate))             # maximum number of iterations 
    ii=0
   
    # initializing progress bar
    with tqdm(total=iter) as pbar:
        while T > T_freez:
            time.sleep(0.1)  
            for i in range(1, int(num_moves)):
                
                jj=area(currSolution,hard_blocks) 
                nextSol,random_num ,block,width_length= perturb(currSolution,hard_blocks,soft_blocks)
                ss=area(nextSol,hard_blocks)
                del_cost = ss- jj
                if acceptMove(del_cost, T,random_num,block,width_length,hard_blocks):
                    currSolution = nextSol
                   
            T = T * cooling_rate        #reducing the temperature  after each iteration after the cooling rate .
            pbar.update(1)
            arealist.append(jj)
    return currSolution

if __name__ == "__main__":
    main()