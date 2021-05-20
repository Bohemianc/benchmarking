with open("sparqls_multi_atoms.txt", encoding="utf-8") as f1, open(
    "sparqls.txt", "w+", encoding="utf-8"
) as f2:
    cnt = 0
    while True:
        buf = f1.readline()
        # print(buf)
        if len(buf) > 0:
            if buf.find(".") == -1:
                cnt += 1
                f2.write(buf)
        else:
            break
    f1.close()
    f2.close()
    print(cnt)

