from pydantic import BaseModel


class Parent(BaseModel):
    parent_attr1: str
    parent_attr2: str

class Child(Parent):
    child_attr1: str
    child_attr2: str

child_ref = Child(parent_attr1="parent_attr1", parent_attr2="parent_attr2", child_attr1="child_attr1", child_attr2="child_attr2")

def lol(parent: Parent):
    print(parent.model_dump())

lol(child_ref)