@nums = global [3 x i32] [i32 5, i32 10, i32 15]

define i32 @main() {
entry:
    %local = alloca i32

    %gptr = getelementptr [3 x i32], ptr @nums, i32 0, i32 1
    %gval = load i32, ptr %gptr

    store i32 %gval, ptr %local

    %value = load i32, ptr %local

    %test = icmp eq i32 %value, 10
    br i1 %test, label %correct, label %wrong

correct:
    ret i32 %value

wrong:
    ret i32 0
}