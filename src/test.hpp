#pragma once

#include <godot_cpp/classes/node.hpp>
#include <godot_cpp/classes/wrapped.hpp>

class Test: public godot::Node{
    GDCLASS(Test, godot::Node)
protected:
    static void _bind_methods();

private:
    void say_hello();
    
};
