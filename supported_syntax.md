### Introducing my markdown flavor\!
## THis is also a header ##

Here's some horizantal rules:

---

-------------------------------------

As you can tell, there's no limit to the length of dashes

Two spaces at the end of a line  
breaks it. Individual paragraphs are seperated by blank lines.

You can also escape markdown's "keywords". For example,
this is a \* astrix, a \\ backslash, a \[ opening bracket, a \! exclamation mark and etc.

You can embed html, for example: \<br\>,
just broke this line. And this is an \<abbr\>Abrreviation\</abbr\>

If you want to use opening and closing angler brackets without 
creating a new element, you can put an ampersand before it. 
Like so: &<, &>.

An ![IMAGE ALT](test.png)
A image link: [![IMAGE ALT](test.png)](url)

This is ***bold and emphasized* [*at the* same time](url.com)**, and this is **bolded**, and this is 
*emphasized* and this is a `inline codeblock`. Notice how bolds and italics use astrixs.

Here's a codeblock:
```c
#include <stdio.h>

int main()
{
    int msg[7] = {'M', 'a', 'g', 'i', 'c', ' ', '!'};
    printf("%s", msg);
}
```

Here's another one:
```
Whoo!!!!!
```

Here's an unordered list:
- ## Headers
- Horizantal rules
- Text stylings
    - **Bolds**
        - *Italics*
    - **Bold**
        - *Italic*
        - *Italic once again*
            - ***Bold and italic***
- Lists
    - > Nested blockquote
        Continuing...
        - Nested once more
            - Nested infinitely.....
                - Test
    - ![Test1](test.png)
    - [Test2](url.com)
- Et voila\!

Nesting occurs via indentation (tabs or 4 spaces if you prefer.)

Here's an ordered list:
+ One 
+ Dos
+ Trois

Here's some both mixed:
- test
- test1
- test2
    + testing1
    + testing2
    + testing3

+ One
    - Two
+ Three

Lists are seperated by blank lines.

*Sighs in struggling to parse lists.*

Here's a blockquote:
> Lorem ipsum
Bla, bla, bla...
> This continue the previous blockquote

> # Boom \- this does not

> - Boom

> > Boom nested

They're seperated by blank lines as well.

Finally, here's a list of references that were helpful in development:
- <https://en.wikipedia.org/wiki/Markdown>
- <https://cs.lmu.edu/~ray/notes/compilerarchitecture>