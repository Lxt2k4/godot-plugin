#include "test.hpp"
#include "godot_cpp/core/class_db.hpp"
#include "godot_cpp/core/print_string.hpp"

using namespace godot;

void Test::say_hello()
{
    print_line("Hello from Test class!");
}

void Test::_bind_methods()
{
    ClassDB::bind_method(D_METHOD("say_hello"), &Test::say_hello);
}
