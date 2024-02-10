#include <iostream>
#include <cmath>
#include <vector>
#include <algorithm>

const double PI = 3.14;
int count_uid = 0;

struct Point
{
    int x;
    int y;

    Point(){}
    Point(int x, int y){this->x = x; this->y = y;}
};

class Shape
{
public:
    size_t get_uid(){return uid;}
    virtual double get_perimetr() = 0;
protected:
    int uid;
};

class Triangle : public Shape
{
public:
    Triangle(Point first, Point second, Point third)
    {
        this->first = first;
        this->second = second;
        this->third = third;
        uid = count_uid;
        count_uid++;
    }

    int side_length(Point first, Point second)
    {
        return (sqrt(pow(second.x - first.x, 2) + pow(second.y - first.y, 2)));
    }

    double get_perimetr() override
    {
        return (side_length(first, second) + side_length(first, third) + side_length(second, third));
    }

private:
    Point first, second, third;
};

class Circle : public Shape
{
public:
    Circle(int r)
    {
        this->r = r;
        uid = count_uid;
        count_uid++;
    }

    double get_perimetr() override
    {
        return (2 * PI * r);
    }

private:
    int r;

};

class Rectangle : public Shape
{
public:
    Rectangle(int width, int height)
    {
        this->width = width;
        this->height = height;
        uid = count_uid;
        count_uid++;
    }

    double get_perimetr() override
    {

        return ((width + height) * 2);
    }

private:
    int width, height;
};


int main()
{
    setlocale(LC_ALL, "Russian");
    std::cout << "Введите кол-во фигур:\n";
    int n; std::cin >> n;
    std::vector<Shape*> v;
    for (int i = 0; i < n; ++i)
    {
        std::string figure_name;
        std::cout << "Введите название фигуры (Rectangle / Triangle / Circle):\n";
        std::cin >> figure_name;
        if (figure_name == "Rectangle")
        {
            int width, height;
            std::cin >> width >> height;
            Rectangle temp_rect(width, height);
            v.push_back(&temp_rect);
        }
        else if (figure_name == "Triangle")
        {
            int x1, y1, x2, y2, x3, y3;
            std::cin >> x1 >> y1 >> x2 >> y2 >> x3 >> y3;
            Triangle temp_triangle(Point(x1, y1), Point(x2, y2), Point(x3, y3));
            v.push_back(&temp_triangle);
        }
        else if (figure_name == "Circle")
        {
            int r;
            std::cin >> r;
            Circle  temp_circle(r);
            v.push_back(&temp_circle);
        }
        else
        {
            std::cout << "Вы ввели что-то неверно!";
        }
    }

    std::cout << "Фигуры в порядке возрастания их периметров (у площади это длина окружности):\n";
    std::sort(v.begin(), v.end(),[](Shape* first, Shape* second){return first->get_perimetr() > second->get_perimetr();});
    for (Shape* element : v)
    {
        std::cout << " " <<  element->get_uid() << " - ";
    }
    return 0;
}

