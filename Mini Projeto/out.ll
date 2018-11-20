define i32 @h(i32, i32) #0 {
   %3 = alloca i32, align 4
   store i32 %0, i32* %3, align 4
   %4 = alloca i32, align 4
   store i32 %1, i32* %4, align 4
   %y = alloca i32, align 4
   %5 = load i32, i32* %4, align 4
   store i32 %5, i32* %y, align 4
   %x = alloca i32, align 4
   store i32 -2, i32* %x, align 4
   %6 = load i32, i32* %y, align 4
   %7 = sub nsw i32 0, %6
   store i32 %7, i32* %x, align 4
   %8 = load i32, i32* %y, align 4
   %9 = sub nsw i32 0, %8
   store i32 %9, i32* %x, align 4
   %10 = load i32, i32* %3, align 4
   ret i32 %10
}

define i32 @main() #0 {
   %x = alloca i32, align 4
   store i32 2, i32* %x, align 4
   %y = alloca i32, align 4
   store i32 4, i32* %y, align 4
   ret i32 0
}

