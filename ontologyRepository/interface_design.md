start:

​												< [GUI-button-new show

​													GUI-button-load show]

GUI-button-new Class:

​	name := ask for new Class name

​	name:										

​												BE-add new class >

​																			MODEL-add new class

​																				classes[name] := Graph()

​												BE-update GUI

​													< make tuples

​													< GUI class list := [new class] 

​		populate class list & show

​		make tree & show

​		



GUI-selectClass(list):

​	shift class

GUI-selectedClass(tree):

​	GUI-button-addItem

​	GUI-button- addPrimitive

​		GUI-list-addInteger

​		GUI-list- addDecimal

​		GUI-list-addComment

​		GUI-list-addURI

​		GUI--list-addBoolean



GUI-selectedClass()



GUI-selectedItem:



GUI-selectedElucidation

GUI-selectedInteger

GUI-selectedString

GUI-selectedComment



​		