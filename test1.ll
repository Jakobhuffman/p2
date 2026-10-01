define i32 @foo() {
entry:
    ret i32 10
}

define i32 @main(i32 %argc) {
entry:
    %x = call i32 @foo()
    %test = icmp eq i32 %x, 10
    br i1 %test, label %good, label %bad

good:
    ret i32 1

bad:
    ret i32 0
}