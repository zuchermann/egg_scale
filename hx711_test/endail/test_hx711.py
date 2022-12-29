from HX711 import SimpleHX711, Rate

with SimpleHX711(5, 6, 384, 37768, Rate.HZ_80) as hx:
    while True:
        print(hx.weight())
