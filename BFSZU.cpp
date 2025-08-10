/*    由22届深大羽协会长Tony Huang(非计算机专业)编写的通用快速抽签分组程序，可应用于日常单项赛或团体赛的抽签分组。
   为了方便其他非IT相关专业的干事使用IDE运行，故仅使用单文件的方式组织。由于2022年校长杯时间较为
   紧迫，故也未应用MFC编程相关知识做成windows应用，设计时也不考虑错误输入的情况。本程序仍有可以改
   进的地方，例如在本程序中单项赛种子选手和轮空选手的分布虽然均匀且随机，是公平的，但未完全按照
   《羽毛球竞赛规则》(2021)中“上、下半区”的相关规定进行排布。
      感谢ChatGPT 3.5为代码加上的注释。如需使用或转发请注明来源于深大羽协
*/
// 引入标准输入输出、时间库、随机数生成、文件流、时间计时器、动态数组、字符串、算法、无序集合库
#include <iostream>
#include <ctime>
#include <random>
#include <fstream>
#include <ctime>
#include <chrono>
#include <vector>
#include <string>
#include <algorithm>
#include <unordered_set>
using namespace std;
#pragma warning(disable : 4996) // 禁用某个编译警告
#define _CRT_SECURE_NO_WARNINGS // 定义宏，表示忽略一些特定的编译器警告
// 定义四个宏，分别表示四个比赛项目：单项赛淘汰赛、单项赛循环赛、团体赛淘汰赛、团体赛循环赛
#define singleGame 1
#define singleGameLoop 2
#define teamGame 3
#define teamGameLoop 4

//定义Draw类
class Draw
{
public:
    char t[32];
    int number = 0;                                                                                       // 单项目参赛人数或队伍总数
    int groupNumber = 0;                                                                                  // 分组数
    int seededNumber = 0;                                                                                 // 种子数
    int roundOneNumber = 0;                                                                               // 第一轮人员总数
    int byeRoundNumber = 0;                                                                               // 第一轮轮空人员总数
    vector<string> name;                                                                                  // 输入的人员名单的一维向量
    vector<int> seededArray;                                                                              // 高水平选手/种子选手一维向量
    vector<int> randomArray;                                                                              // 储存不重复随机数的一维向量
    vector<string> seededName;                                                                            // 高水平选手/种子选手名单一维向量
    vector<vector<int>> groupArray;                                                                       // 总抽签结果二维向量
    vector<vector<int>> byeRoundArray;                                                                    // 第一轮轮空选手名单二维向量
    vector<vector<int>> roundOneArray;                                                                    // 第一轮人员名单二维向量
    void generation(int option);                                                                          // 抽签分组生成函数
    void randomNumGenerator(vector<int> &Array, int num);                                                 // 生成随机数并存入向量的函数
    vector<vector<int>> divideArray(vector<int> &nums, int m);                                            // 将向量中的元素分成m份，任意相邻两份之间元素个数相差不超过1
    void printList(ofstream &out_file, string note, vector<vector<int>> &Array);                          // 打印名单并输出到文件
    vector<vector<int>> Select(const vector<vector<int>> &tempNameArray, int byeRoundNumber);             // 从一个二维向量的每一行均匀抽取特定个元素组成二维向量
    void distributeElements(const vector<int> &seededArray, vector<vector<int>> &tempNameArray);          // 随机且均匀地将前者向量中的元素分配在后者每一行向量中
    vector<vector<int>> deleteSameElements(vector<vector<int>> temp, vector<vector<int>> byeRoundNumber); // 将两个二维向量中的不同元素相减的函数
    char *getTime()                                                                                       // 定义名为 getTime 的字符指针函数，用于获取系统当前时间
    {
        time_t NowTime = time(0);                          // 获取当前系统时间，并将时间赋值给名为 NowTime 的 time_t 类型变量
        strftime(t, sizeof(t), "%c", localtime(&NowTime)); // 使用 strftime 函数将时间格式化，并将结果存储到名为 t 的字符数组中
        return t;                                          // 返回存储时间的字符数组指针
    }
};

// 定义名为 cmp 的 bool 类型函数，用于比较两个 vector 容器的大小
bool cmp(const vector<int> &a, const vector<int> &b)
{
    return a.size() < b.size(); // 返回 a 容器大小是否小于 b 容器大小的布尔值，用于排序等操作
}

// 定义名为 find 的 bool 类型函数，用于在 vector 容器中查找指定的元素
bool find(int num, vector<int> vec) 
{
    for (int i = 0; i < vec.size(); i++) // 遍历 vector 容器中的所有元素
        if (vec[i] == num)               // 判断当前元素是否等于指定的元素
            return true;                 // 若相等，则返回 true
    return false;                        // 若遍历完整个容器仍未找到，则返回 false
}

// 定义名为 countNonEmpty 的整型函数，用于计算 vector 容器中非空字符串的个数
int countNonEmpty(const vector<string> &vec) 
{
    int count = 0;              // 初始化计数器为 0
    for (const auto &str : vec) // 使用范围 for 循环遍历 vector 容器中的所有元素
        if (!str.empty())       // 判断当前字符串是否为空
            count++;            // 若不为空，则计数器加 1
    return count;               // 返回计数器值，即非空字符串的个数
}

// 定义名为 divideArray 的函数，返回值为一个二维 vector 容器，用于将一个一维 vector 容器 nums 划分为 m 个子数组
vector<vector<int>> Draw::divideArray(vector<int> &nums, int m) 
{
    int n = nums.size();                              // 获取 nums 容器的大小
    vector<vector<int>> res(m);                       // 定义一个二维 vector 容器 res，容量为 m，每个子容器也是一个 vector<int> 类型，用于存储子数组
    int i = 0;                                        // 初始化 i 为 0
    for (int j = 0; j < m; j++)                       // 遍历 0 到 m - 1 的每一个整数 j
        for (int k = 0; k < n / m + (j < n % m); k++) // 遍历 0 到 n / m + (j < n % m) - 1 的每一个整数 k，其中 j < n % m 表示前 n % m 个子数组中的每个子数组多加一个元素
            res[j].push_back(nums[i++]);              // 将 nums 中的元素按照顺序分配给子数组 res[j]
    return res;                                       // 返回划分后的子数组容器
}

// 定义名为 deleteSameElements 的函数，返回值为一个二维 vector 容器，用于删除 temp 和 byeRoundNumber 中相同的元素
vector<vector<int>> Draw::deleteSameElements(vector<vector<int>> temp, vector<vector<int>> byeRoundNumber) 
{
    vector<vector<int>> result;                           // 定义一个二维 vector 容器 result，用于存储删除相同元素后的子数组
    result.resize(temp.size());                           // 将 result 的容量调整为 temp 的大小
    for (int i = 0; i < temp.size(); i++)                 // 遍历 temp 的每一个子数组
        if (temp[i].size() != byeRoundNumber[i].size())   // 判断 temp 和 byeRoundNumber 中的子数组长度是否相同
            for (int j = 0; j < temp[i].size(); j++)      // 遍历 temp 中当前子数组的每一个元素
                if (!find(temp[i][j], byeRoundNumber[i])) // 如果当前元素不在 byeRoundNumber 的当前子数组中
                    result[i].push_back(temp[i][j]);      // 将该元素添加到 result 中的当前子数组中
    return result;                                        // 返回删除相同元素后的子数组容器
}

// 定义名为 Select 的函数，返回值为一个二维 vector 容器，用于从 tempNameArray 中均匀抽取 byeRoundNumber 个元素
vector<vector<int>> Draw::Select(const vector<vector<int>> &tempNameArray, int byeRoundNumber)
{
    // 创建一个二维 vector res，其行数等于 tempNameArray 的行数，列数等于 byeRoundNumber / tempNameArray 的行数。
    vector<vector<int>> res(tempNameArray.size(), vector<int>(byeRoundNumber / tempNameArray.size()));

    // 用变量 remainder 记录除法的余数。
    int remainder = byeRoundNumber % tempNameArray.size();

    // 对每一行进行循环。
    for (int i = 0; i < tempNameArray.size(); ++i)
    {
        // 创建一个一维 vector，其元素是 tempNameArray[i] 的下标。
        vector<int> indices(tempNameArray[i].size());
        for (int j = 0; j < indices.size(); ++j)
            indices[j] = j;

        // 从 tempNameArray[i] 中选择 res[i] 的元素，即将 indices[j] 对应的 tempNameArray[i][indices[j]] 赋值给 res[i][j]。
        for (int j = 0; j < res[i].size(); ++j)
            res[i][j] = tempNameArray[i][indices[j]];

        // 如果 i 小于 remainder，则在 res[i] 的末尾添加 tempNameArray[i][indices[res[i].size()]]。
        if (i < remainder)
            res[i].push_back(tempNameArray[i][indices[res[i].size()]]);
    }

    // 返回结果二维 vector。
    return res;
}

// 定义名为 existed 的函数，返回值为 bool 类型，用于判断 index 是否存在于 inputArray 中。
bool existed(int index, vector<int> &inputArray, int num)
{
    // 遍历 inputArray 数组，查找是否存在 index 这个元素
    for (int i = 0; i < num; i++)
        if (index == inputArray[i])
            return true;
    // 如果不存在 index 这个元素，返回 false
    return false;
}

// 定义名为 randomNumGenerator 的函数，返回值为空，用于生成随机数并存入 Array 中。
void Draw::randomNumGenerator(vector<int> &Array, int num)
{
    int n = 0, m = num - 1;
    // 如果 Array 数组等于 seededArray 数组，则生成 [number, number+seededNumber-1] 范围内的随机数
    if (Array == seededArray)
    {
        n = number;
        m = number + seededNumber - 1;
    }
    // 使用当前时间作为 mt19937 随机数生成器的种子
    mt19937 rng(std::chrono::system_clock::now().time_since_epoch().count());
    for (int i = 0; i < num; i++)
    {
        // 随机生成位于 [n, m] 范围内的整数
        uniform_int_distribution<> dis(n, m);
        int random_num = dis(rng);
        // 如果生成的随机数已经存在于 Array 数组中，就一直生成新的随机数，直到生成的随机数不再存在于 Array 数组中
        while (existed(random_num, Array, i))
            random_num = dis(rng);
        Array[i] = random_num; // 将生成的随机数存储在 Array 数组中，体现随机性&公正性
    }
}

// 定义名为 distributeElements 的函数，返回值为空，用于将 seededArray 中的元素分配到 tempNameArray 中。
void Draw::distributeElements(const vector<int> &seededArray, vector<vector<int>> &tempNameArray)
{
    random_device rd;  // 随机设备，用于产生随机种子
    mt19937 gen(rd()); // 用随机设备生成初始种子
    int numRows = tempNameArray.size();
    for (int i = 0; i < seededArray.size(); i++) // 循环遍历种子数组中的元素
    {
        int rowIndex = i % numRows;
        tempNameArray[rowIndex].push_back(seededArray[i]); // 将当前种子元素添加到 tempNameArray 的第 i % numRows 行末尾
    }
    // 对每一行的元素进行随机排序
    for (int i = 0; i < numRows; i++)
    {
        shuffle(tempNameArray[i].begin(), tempNameArray[i].end(), gen);
    }
}

// 定义名为 Draw::generation 的函数，返回值为空，用于生成抽签结果。
void Draw::generation(int option)
{
    ofstream out_file("抽签结果.txt");       // 打开文件流，写入文件名
    vector<int> randomArray(number);         // 定义一个长度为number的int类型向量randomArray
    randomNumGenerator(randomArray, number); // 调用randomNumGenerator函数生成随机数向量
    if (seededNumber != 0)                   // 如果设定了种子号码
    {
        seededArray.resize(seededNumber);              // 改变种子数组大小以适应种子数量
        randomNumGenerator(seededArray, seededNumber); // 生成种子随机数
        for (int i = 0; i < seededName.size(); i++)    // 遍历种子名单
            name.push_back(seededName[i]);             // 将名字加入总名单
        number = number + seededNumber;                // 增加总人数
    }
    vector<vector<int>> tempNameArray;                     // 定义一个二维向量tempNameArray，用于存储由随机数生成的临时分组名单
    tempNameArray = divideArray(randomArray, groupNumber); // 调用divideArray函数，将随机数分成groupNumber个小组，返回分组结果
    sort(tempNameArray.begin(), tempNameArray.end(), cmp); // 将分组结果按照人数从多到少排序
    distributeElements(seededArray, tempNameArray);        // 将种子随机插入分组结果中
    sort(tempNameArray.begin(), tempNameArray.end(), cmp);
    if (option == singleGameLoop || option == teamGameLoop)       // 如果是循环赛或团队赛
        printList(out_file, "\n总分组结果如下：", tempNameArray); // 输出总抽签结果
    if (option == singleGame || option == teamGame)               // 如果是普通赛或团队赛
    {
        int i = 0, oddGroup = 0, oddGroupNum = 0, evenGroupNum = 0, evenGroup = 0; // 初始化计数器
        for (auto vec : tempNameArray)                                             // 遍历分组结果
        {
            if (tempNameArray[i].size() % 2 != 0) // 如果小组人数为奇数
            {
                oddGroup++;                            // 计算奇数小组数量
                oddGroupNum = tempNameArray[i].size(); // 记录奇数小组人数
            }
            if (tempNameArray[i].size() % 2 == 0) // 如果小组人数为偶数
            {
                evenGroup++;                            // 计算偶数小组数量
                evenGroupNum = tempNameArray[i].size(); // 记录偶数小组人数
            }
            i++; // 计数器自增
        }
        /*核心思想*/
        i=0;
        for (; pow(2, i) < evenGroupNum || pow(2, i) == evenGroupNum; i++)
        {
            if (pow(2, i) > evenGroupNum)
                break;
        }
        int gap=evenGroupNum-pow(2,i-1);//算出人数为偶数的小组的人数距离比其小但又最接近的2的n次幂的差值
        if(gap!=0)//差值不为零，说明人数为偶数的小组的人数因式分解后会有奇数
        //偶数小组人数大于奇数小组人数，附加赛人数=差值*偶数小组数*2+(差值-1)*奇数小组数*2,若小于等于则=差值*偶数小组数*2+(差值+1)*奇数小组数*2
        roundOneNumber = (oddGroupNum < evenGroupNum) ? gap*2*evenGroup + (gap-1)*2*oddGroup : gap*2*evenGroup +(gap+1)*2*oddGroup;
        /*差值为零，说明人数为偶数的小组的人数是2的n次方，偶数小组人数大于奇数小组人数，附加赛人数=2*奇数小组人数*奇数小组人数与
          比其小但又最接近的2的n次幂的差值，否则为奇数小组数*2 */
        else roundOneNumber = (oddGroupNum < evenGroupNum) ? 2*oddGroup*(oddGroupNum-pow(2,i-2)):oddGroup*2;
        byeRoundNumber = number - roundOneNumber;                         // 计算无需参与比赛的人数，即轮空人数
        byeRoundArray = Select(tempNameArray, byeRoundNumber);            // 在所有的人员中随机选出 byeRoundNumber 个人作为轮空人员，生成一个名为 byeRoundArray 的二维向量
        roundOneArray = deleteSameElements(tempNameArray, byeRoundArray); // 在所有的人员中去掉轮空人员，生成一个名为 roundOneArray 的二维向量
        groupArray = roundOneArray;                                       // 将 roundOneArray 复制到 groupArray，这样可以避免 roundOneArray 被修改时影响到 groupArray
        /*将每个轮空小组中的人员插入到第一轮小组中，生成一个新的名为 groupArray 的二维向量，
        其中每个一维向量表示一个比赛小组，包含需要参与比赛的人员和轮空的人员。*/
        for (int i = 0; i < groupArray.size() && i < byeRoundArray.size(); i++)
            groupArray[i].insert(groupArray[i].end(), byeRoundArray[i].begin(), byeRoundArray[i].end());
        printList(out_file, "\n第一轮轮空名单如下：", byeRoundArray); // 打印第一轮轮空名单
        printList(out_file, "\n第一轮对阵名单如下：", roundOneArray); // 打印第一轮对阵名单
        printList(out_file, "\n总分组结果如下：", groupArray);        // 打印总分组结果
    }
    out_file.close();
}

// 定义名为 printList 的函数，返回值为空，用于打印名单并输出到文件。
void Draw::printList(ofstream &out_file, string note, vector<vector<int>> &Array)
{
    vector<vector<string>> List;           // 定义一个二维字符串向量 List
    for (int i = 0; i < Array.size(); i++) // 遍历整数向量 Array 的元素
    {
        vector<string> row;                       // 定义一个字符串向量 row
        for (int j = 0; j < Array[i].size(); j++) // 遍历整数向量 Array[i] 的元素
        {
            row.push_back(name[Array[i][j]]); // 向 row 向量末尾添加 name[Array[i][j]]
        }
        List.push_back(row); // 将 row 向量添加到 List 向量末尾
    }
    for (int i = 0; i <= 90; i++) // 输出 90 个下划线
        cout << "_";
    cout << note << endl;     // 输出 note 并换行
    out_file << note << endl; // 向输出文件中写入 note 并换行
    int i = 0;                // 初始化 i 为 0
    for (auto vec : List)     // 遍历二维字符串向量 List 的每一个向量
    {
        cout << "第 " << i + 1 << " 组"                  // 输出组号
             << "(" << countNonEmpty(List[i]) << ")"     // 输出当前组的非空元素数量
             << ":";                                     // 输出冒号
        out_file << "第 " << i + 1 << " 组"              // 向输出文件中写入组号
                 << "(" << countNonEmpty(List[i]) << ")" // 向输出文件中写入当前组的非空元素数量
                 << ":";                                 // 向输出文件中写入冒号
        for (auto str : vec)                             // 遍历当前向量中的每一个字符串
        {
            out_file << str << " "; // 向输出文件中写入当前字符串
            cout << str << " ";     // 输出当前字符串并在末尾添加一个空格
        }
        out_file << endl; // 向输出文件中换行
        cout << endl;     // 输出一个空行
        i++;              // i 自增 1
    }
    i = 0;                   // 将 i 重置为 0
    if (Array == groupArray) // 如果分组结果与第一轮后分组结果相同，即所有选手都参与了比赛，以方便深大羽协策划部编排Excel对阵表的格式输出总名单
    {
        cin.get(); // 吸收回车
        cout << "按任意键则以适合编排Excel对阵表的形式输出" << endl;
        cin.get();
        for (auto vec : List) // 遍历分组结果
        {
            cout << "\n第 " << i + 1 << " 组"
                 << "(" << countNonEmpty(List[i]) << ")\n"; // 输出分组序号和每组人数

            out_file << "\n第 " << i + 1 << " 组"
                     << "(" << countNonEmpty(List[i]) << ")\n";

            for (auto str : vec) // 遍历每组的选手姓名
            {
                out_file << str << endl
                         << endl; // 输出每个选手姓名到文件中
                cout << str << endl
                     << endl; // 输出每个选手姓名到控制台中
            }
            out_file << endl;
            cout << endl;
            i++;
        }
    }
    cout << "生成于：" << getTime() << endl;
    out_file << "生成于：" << getTime() << endl; // 输出生成时间到文件和控制台
}

int main()
{
    Draw dr; // 创建 Draw 类对象 dr，用于执行抽签操作。
    int gameOption = 0, eventOption = 1;
    cout << "本程序设计时不考虑任何错误输入的情况，如果有错误输入请关闭并重新运行" << endl;
    cout << "请输入对应数字选择项目: 1 单项赛(淘汰赛) 2 单项赛(循环赛) 3 团体赛(淘汰赛) 4 团体赛(循环赛) 其余任意键 结束\n"; // 输出抽签项目选项
    cin >> gameOption;                                                                                                       // 等待用户输入选项
    if (gameOption == singleGame || gameOption == singleGameLoop)                                                            // 如果用户选择单项赛淘汰赛或单项赛循环赛
    {
        cout << "请输入对应数字选择项目: 1 单打 2双打 其余任意键 结束\n";
        cin >> eventOption;
        if (eventOption == 1)
            cout << "请输入单打人数(在设立种子时为非种子数)："; // 提示用户输入比赛人数或非种子选手人数
        else if (eventOption == 2)
            cout << "请输入双打组合数(在设立种子时为非种子数)：";
        else
            return 0;
    }
    else if (gameOption == teamGameLoop || gameOption == teamGame) // 如果用户选择团体赛淘汰赛或团体赛循环赛
        cout << "请输入队伍数(在设立种子时为非种子数)：";          // 要求用户输入队伍数
    else
        return 0;
    cin >> dr.number;                              // 读入比赛人数或非种子选手人数
    cin.get();                                     // 吸收回车
    dr.name.resize(dr.number);                     // 为 dr.name 向量分配内存
    cout << "\n请输入种子数（若不设立则输入0）："; // 提示用户输入种子数
    cin >> dr.seededNumber;                        // 读入种子数
    cin.get();                                     // 吸收回车
    dr.seededName.resize(dr.seededNumber);         // 为 dr.seededName 向量分配内存
    if (eventOption != 2)
    {
        cout << "请 按列 输入名单：" << endl; // 提示用户输入每个人的名字
        for (int i = 0; i < dr.number; i++)   // 依次读入每个人的名字
            getline(cin, dr.name[i]);
        if (dr.seededNumber != 0) // 如果有种子选手
        {
            cout << "请 按列 输入种子名单：" << endl; // 提示用户输入每个种子选手的名字
            for (int i = 0; i < dr.seededNumber; i++) // 依次读入每个种子选手的名字
                getline(cin, dr.seededName[i]);
        }
    }
    if (eventOption == 2)
    {
        vector<string> temp;
        temp.resize(dr.number);
        cout << "请 按列 输入双打第一列选手名单：" << endl; // 提示用户输入每个人的名字
        for (int i = 0; i < dr.number; i++)                 // 依次读入每个人的名字
            getline(cin, dr.name[i]);
        cout << "请 按列 输入双打第一列选手的队友名单：" << endl; // 提示用户输入每个人的名字
        for (int i = 0; i < dr.number; i++)                       // 依次读入每个人的名字
        {
            getline(cin, temp[i]);
            dr.name[i] = "[" + dr.name[i] + " " + temp[i] + "]";
        }
        if (dr.seededNumber != 0) // 如果有种子选手
        {
            temp.clear();
            temp.resize(dr.seededNumber);
            cout << "请 按列 输入双打种子第一列选手名单：" << endl; // 提示用户输入每个种子选手的名字
            for (int i = 0; i < dr.seededNumber; i++) // 依次读入每个种子选手的名字
                getline(cin, temp[i]);
            cout << "请 按列 输入双打种子第一列选手的队友名单：" << endl; // 提示用户输入每个种子选手的名字
            for (int i = 0; i < dr.seededNumber; i++) // 依次读入每个种子选手的名字
            {    
                getline(cin, dr.seededName[i]);
                dr.seededName[i]="[" + dr.seededName[i] + " " + temp[i] + "]";
            }
        }
    }
    cout << "请输入小组的个数：";
    cin >> dr.groupNumber;     // 要求用户输入小组的个数，并将其存储到 dr.groupNumber 变量中
    dr.generation(gameOption); // 调用 dr.generation(option) 函数，生成比赛名单，进行抽签操作
    system("pause");           // 最后调用 system("pause") 函数，使程序暂停运行，直到用户按下任意键继续执行
}
