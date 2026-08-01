import time


"""
STATE = dirty clothes

move the clothes to the laundry

sort the clothes by colors

pick the correct soap
put water in the machine
add the soap
get the clothes with brighter color
dump them in the machine
turn on the machine

wait for 30 minutes

turn off the machine

get the clothes out of the machine

if the water is still clean
    use the same water to wash the colored clothes
if not
    put water in the machine
    add soap

dump the next set of clothes in the machine

turn on the machine

wait for another 30 minutes

turn off the machine

drain the water

rinse the first set of clothes

repeat the last step x times

rinse the second set of clothes

repeat the last step x times

wring the clothes

hang them on the lines

END STATE = clean clothes
"""


dirty_clothes_basket = [
    "black_shirt",
    "white_short",
    "blue_jean_short",
    "white_singlet",
    "red_jacket"
]

print("\nTaking my dirty clothes to the laundry")

bright_dirty_clothes_group = []
dull_dirty_clothes_group = []

print("\nStart sorting by color")

for cloth in dirty_clothes_basket:
    if cloth.__contains__("white"):
        bright_dirty_clothes_group.append(cloth)
    else:
        dull_dirty_clothes_group.append(cloth)

print("I have finished sorting by color")


soap = "Klin"

print(f"\nPicking {soap} soap")

print("Pouring water into the machine")
print(f"Adding {soap} soap")

print("Putting the bright clothes in the machine")
print("Turning on the washing machine")

time.sleep(5)   # waiting for the machine to wash for 30 minutes

print("Turning off the machine")
print("Removing the bright clothes from the machine")


water_is_clean = False

if water_is_clean:
    print("\nWater is still clean, reusing it")
else:
    print("\nDraining the dirty water")
    print("Pouring clean water into the machine")
    print(f"Adding {soap} soap")


print("Putting the colored clothes in the machine")
print("Turning on the washing machine")

time.sleep(5)   # waiting for another 30 minutes

print("Turning off the machine")

print("Draining the water")


print("\nRinsing the bright clothes")

for rinse in range(3):
    print(f"Rinse {rinse + 1}")

print("Finished rinsing the bright clothes")


print("\nRinsing the colored clothes")

for rinse in range(3):
    print(f"Rinse {rinse + 1}")

print("Finished rinsing the colored clothes")


print("\nWringing all the clothes")

clean_clothes = []

for cloth in bright_dirty_clothes_group:
    print(f"Wringing {cloth}")
    clean_clothes.append(cloth)

for cloth in dull_dirty_clothes_group:
    print(f"Wringing {cloth}")
    clean_clothes.append(cloth)


print("\nHanging the clothes on the line")

for cloth in clean_clothes:
    print(f"Hanging {cloth}")


print("\nEND STATE = clean clothes")