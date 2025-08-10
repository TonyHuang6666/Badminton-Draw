/*    ��22�������Э�᳤Tony Huang(�Ǽ����רҵ)��д��ͨ�ÿ��ٳ�ǩ������򣬿�Ӧ�����ճ����������������ĳ�ǩ���顣
   Ϊ�˷���������IT���רҵ�ĸ���ʹ��IDE���У��ʽ�ʹ�õ��ļ��ķ�ʽ��֯������2022��У����ʱ���Ϊ
   ���ȣ���ҲδӦ��MFC������֪ʶ����windowsӦ�ã����ʱҲ�����Ǵ����������������������п��Ը�
   ���ĵط��������ڱ������е���������ѡ�ֺ��ֿ�ѡ�ֵķֲ���Ȼ������������ǹ�ƽ�ģ���δ��ȫ����
   ����ë��������(2021)�С��ϡ��°���������ع涨�����Ų���
      ��лChatGPT 3.5Ϊ������ϵ�ע�͡�����ʹ�û�ת����ע����Դ�������Э
*/
// �����׼���������ʱ��⡢��������ɡ��ļ�����ʱ���ʱ������̬���顢�ַ������㷨�����򼯺Ͽ�
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
#pragma warning(disable : 4996) // ����ĳ�����뾯��
#define _CRT_SECURE_NO_WARNINGS // ����꣬��ʾ����һЩ�ض��ı���������
// �����ĸ��꣬�ֱ��ʾ�ĸ�������Ŀ����������̭����������ѭ��������������̭����������ѭ����
#define singleGame 1
#define singleGameLoop 2
#define teamGame 3
#define teamGameLoop 4

//����Draw��
class Draw
{
public:
    char t[32];
    int number = 0;                                                                                       // ����Ŀ�����������������
    int groupNumber = 0;                                                                                  // ������
    int seededNumber = 0;                                                                                 // ������
    int roundOneNumber = 0;                                                                               // ��һ����Ա����
    int byeRoundNumber = 0;                                                                               // ��һ���ֿ���Ա����
    vector<string> name;                                                                                  // �������Ա������һά����
    vector<int> seededArray;                                                                              // ��ˮƽѡ��/����ѡ��һά����
    vector<int> randomArray;                                                                              // ���治�ظ��������һά����
    vector<string> seededName;                                                                            // ��ˮƽѡ��/����ѡ������һά����
    vector<vector<int>> groupArray;                                                                       // �ܳ�ǩ�����ά����
    vector<vector<int>> byeRoundArray;                                                                    // ��һ���ֿ�ѡ��������ά����
    vector<vector<int>> roundOneArray;                                                                    // ��һ����Ա������ά����
    void generation(int option);                                                                          // ��ǩ�������ɺ���
    void randomNumGenerator(vector<int> &Array, int num);                                                 // ��������������������ĺ���
    vector<vector<int>> divideArray(vector<int> &nums, int m);                                            // �������е�Ԫ�طֳ�m�ݣ�������������֮��Ԫ�ظ���������1
    void printList(ofstream &out_file, string note, vector<vector<int>> &Array);                          // ��ӡ������������ļ�
    vector<vector<int>> Select(const vector<vector<int>> &tempNameArray, int byeRoundNumber);             // ��һ����ά������ÿһ�о��ȳ�ȡ�ض���Ԫ����ɶ�ά����
    void distributeElements(const vector<int> &seededArray, vector<vector<int>> &tempNameArray);          // ����Ҿ��ȵؽ�ǰ�������е�Ԫ�ط����ں���ÿһ��������
    vector<vector<int>> deleteSameElements(vector<vector<int>> temp, vector<vector<int>> byeRoundNumber); // ��������ά�����еĲ�ͬԪ������ĺ���
    char *getTime()                                                                                       // ������Ϊ getTime ���ַ�ָ�뺯�������ڻ�ȡϵͳ��ǰʱ��
    {
        time_t NowTime = time(0);                          // ��ȡ��ǰϵͳʱ�䣬����ʱ�丳ֵ����Ϊ NowTime �� time_t ���ͱ���
        strftime(t, sizeof(t), "%c", localtime(&NowTime)); // ʹ�� strftime ������ʱ���ʽ������������洢����Ϊ t ���ַ�������
        return t;                                          // ���ش洢ʱ����ַ�����ָ��
    }
};

// ������Ϊ cmp �� bool ���ͺ��������ڱȽ����� vector �����Ĵ�С
bool cmp(const vector<int> &a, const vector<int> &b)
{
    return a.size() < b.size(); // ���� a ������С�Ƿ�С�� b ������С�Ĳ���ֵ����������Ȳ���
}

// ������Ϊ find �� bool ���ͺ����������� vector �����в���ָ����Ԫ��
bool find(int num, vector<int> vec) 
{
    for (int i = 0; i < vec.size(); i++) // ���� vector �����е�����Ԫ��
        if (vec[i] == num)               // �жϵ�ǰԪ���Ƿ����ָ����Ԫ��
            return true;                 // ����ȣ��򷵻� true
    return false;                        // ������������������δ�ҵ����򷵻� false
}

// ������Ϊ countNonEmpty �����ͺ��������ڼ��� vector �����зǿ��ַ����ĸ���
int countNonEmpty(const vector<string> &vec) 
{
    int count = 0;              // ��ʼ��������Ϊ 0
    for (const auto &str : vec) // ʹ�÷�Χ for ѭ������ vector �����е�����Ԫ��
        if (!str.empty())       // �жϵ�ǰ�ַ����Ƿ�Ϊ��
            count++;            // ����Ϊ�գ���������� 1
    return count;               // ���ؼ�����ֵ�����ǿ��ַ����ĸ���
}

// ������Ϊ divideArray �ĺ���������ֵΪһ����ά vector ���������ڽ�һ��һά vector ���� nums ����Ϊ m ��������
vector<vector<int>> Draw::divideArray(vector<int> &nums, int m) 
{
    int n = nums.size();                              // ��ȡ nums �����Ĵ�С
    vector<vector<int>> res(m);                       // ����һ����ά vector ���� res������Ϊ m��ÿ��������Ҳ��һ�� vector<int> ���ͣ����ڴ洢������
    int i = 0;                                        // ��ʼ�� i Ϊ 0
    for (int j = 0; j < m; j++)                       // ���� 0 �� m - 1 ��ÿһ������ j
        for (int k = 0; k < n / m + (j < n % m); k++) // ���� 0 �� n / m + (j < n % m) - 1 ��ÿһ������ k������ j < n % m ��ʾǰ n % m ���������е�ÿ����������һ��Ԫ��
            res[j].push_back(nums[i++]);              // �� nums �е�Ԫ�ذ���˳������������ res[j]
    return res;                                       // ���ػ��ֺ������������
}

// ������Ϊ deleteSameElements �ĺ���������ֵΪһ����ά vector ����������ɾ�� temp �� byeRoundNumber ����ͬ��Ԫ��
vector<vector<int>> Draw::deleteSameElements(vector<vector<int>> temp, vector<vector<int>> byeRoundNumber) 
{
    vector<vector<int>> result;                           // ����һ����ά vector ���� result�����ڴ洢ɾ����ͬԪ�غ��������
    result.resize(temp.size());                           // �� result ����������Ϊ temp �Ĵ�С
    for (int i = 0; i < temp.size(); i++)                 // ���� temp ��ÿһ��������
        if (temp[i].size() != byeRoundNumber[i].size())   // �ж� temp �� byeRoundNumber �е������鳤���Ƿ���ͬ
            for (int j = 0; j < temp[i].size(); j++)      // ���� temp �е�ǰ�������ÿһ��Ԫ��
                if (!find(temp[i][j], byeRoundNumber[i])) // �����ǰԪ�ز��� byeRoundNumber �ĵ�ǰ��������
                    result[i].push_back(temp[i][j]);      // ����Ԫ����ӵ� result �еĵ�ǰ��������
    return result;                                        // ����ɾ����ͬԪ�غ������������
}

// ������Ϊ Select �ĺ���������ֵΪһ����ά vector ���������ڴ� tempNameArray �о��ȳ�ȡ byeRoundNumber ��Ԫ��
vector<vector<int>> Draw::Select(const vector<vector<int>> &tempNameArray, int byeRoundNumber)
{
    // ����һ����ά vector res������������ tempNameArray ���������������� byeRoundNumber / tempNameArray ��������
    vector<vector<int>> res(tempNameArray.size(), vector<int>(byeRoundNumber / tempNameArray.size()));

    // �ñ��� remainder ��¼������������
    int remainder = byeRoundNumber % tempNameArray.size();

    // ��ÿһ�н���ѭ����
    for (int i = 0; i < tempNameArray.size(); ++i)
    {
        // ����һ��һά vector����Ԫ���� tempNameArray[i] ���±ꡣ
        vector<int> indices(tempNameArray[i].size());
        for (int j = 0; j < indices.size(); ++j)
            indices[j] = j;

        // �� tempNameArray[i] ��ѡ�� res[i] ��Ԫ�أ����� indices[j] ��Ӧ�� tempNameArray[i][indices[j]] ��ֵ�� res[i][j]��
        for (int j = 0; j < res[i].size(); ++j)
            res[i][j] = tempNameArray[i][indices[j]];

        // ��� i С�� remainder������ res[i] ��ĩβ��� tempNameArray[i][indices[res[i].size()]]��
        if (i < remainder)
            res[i].push_back(tempNameArray[i][indices[res[i].size()]]);
    }

    // ���ؽ����ά vector��
    return res;
}

// ������Ϊ existed �ĺ���������ֵΪ bool ���ͣ������ж� index �Ƿ������ inputArray �С�
bool existed(int index, vector<int> &inputArray, int num)
{
    // ���� inputArray ���飬�����Ƿ���� index ���Ԫ��
    for (int i = 0; i < num; i++)
        if (index == inputArray[i])
            return true;
    // ��������� index ���Ԫ�أ����� false
    return false;
}

// ������Ϊ randomNumGenerator �ĺ���������ֵΪ�գ�������������������� Array �С�
void Draw::randomNumGenerator(vector<int> &Array, int num)
{
    int n = 0, m = num - 1;
    // ��� Array ������� seededArray ���飬������ [number, number+seededNumber-1] ��Χ�ڵ������
    if (Array == seededArray)
    {
        n = number;
        m = number + seededNumber - 1;
    }
    // ʹ�õ�ǰʱ����Ϊ mt19937 �����������������
    mt19937 rng(std::chrono::system_clock::now().time_since_epoch().count());
    for (int i = 0; i < num; i++)
    {
        // �������λ�� [n, m] ��Χ�ڵ�����
        uniform_int_distribution<> dis(n, m);
        int random_num = dis(rng);
        // ������ɵ�������Ѿ������� Array �����У���һֱ�����µ��������ֱ�����ɵ���������ٴ����� Array ������
        while (existed(random_num, Array, i))
            random_num = dis(rng);
        Array[i] = random_num; // �����ɵ�������洢�� Array �����У����������&������
    }
}

// ������Ϊ distributeElements �ĺ���������ֵΪ�գ����ڽ� seededArray �е�Ԫ�ط��䵽 tempNameArray �С�
void Draw::distributeElements(const vector<int> &seededArray, vector<vector<int>> &tempNameArray)
{
    random_device rd;  // ����豸�����ڲ����������
    mt19937 gen(rd()); // ������豸���ɳ�ʼ����
    int numRows = tempNameArray.size();
    for (int i = 0; i < seededArray.size(); i++) // ѭ���������������е�Ԫ��
    {
        int rowIndex = i % numRows;
        tempNameArray[rowIndex].push_back(seededArray[i]); // ����ǰ����Ԫ����ӵ� tempNameArray �ĵ� i % numRows ��ĩβ
    }
    // ��ÿһ�е�Ԫ�ؽ����������
    for (int i = 0; i < numRows; i++)
    {
        shuffle(tempNameArray[i].begin(), tempNameArray[i].end(), gen);
    }
}

// ������Ϊ Draw::generation �ĺ���������ֵΪ�գ��������ɳ�ǩ�����
void Draw::generation(int option)
{
    ofstream out_file("��ǩ���.txt");       // ���ļ�����д���ļ���
    vector<int> randomArray(number);         // ����һ������Ϊnumber��int��������randomArray
    randomNumGenerator(randomArray, number); // ����randomNumGenerator�����������������
    if (seededNumber != 0)                   // ����趨�����Ӻ���
    {
        seededArray.resize(seededNumber);              // �ı����������С����Ӧ��������
        randomNumGenerator(seededArray, seededNumber); // �������������
        for (int i = 0; i < seededName.size(); i++)    // ������������
            name.push_back(seededName[i]);             // �����ּ���������
        number = number + seededNumber;                // ����������
    }
    vector<vector<int>> tempNameArray;                     // ����һ����ά����tempNameArray�����ڴ洢����������ɵ���ʱ��������
    tempNameArray = divideArray(randomArray, groupNumber); // ����divideArray��������������ֳ�groupNumber��С�飬���ط�����
    sort(tempNameArray.begin(), tempNameArray.end(), cmp); // �����������������Ӷൽ������
    distributeElements(seededArray, tempNameArray);        // ��������������������
    sort(tempNameArray.begin(), tempNameArray.end(), cmp);
    if (option == singleGameLoop || option == teamGameLoop)       // �����ѭ�������Ŷ���
        printList(out_file, "\n�ܷ��������£�", tempNameArray); // ����ܳ�ǩ���
    if (option == singleGame || option == teamGame)               // �������ͨ�����Ŷ���
    {
        int i = 0, oddGroup = 0, oddGroupNum = 0, evenGroupNum = 0, evenGroup = 0; // ��ʼ��������
        for (auto vec : tempNameArray)                                             // ����������
        {
            if (tempNameArray[i].size() % 2 != 0) // ���С������Ϊ����
            {
                oddGroup++;                            // ��������С������
                oddGroupNum = tempNameArray[i].size(); // ��¼����С������
            }
            if (tempNameArray[i].size() % 2 == 0) // ���С������Ϊż��
            {
                evenGroup++;                            // ����ż��С������
                evenGroupNum = tempNameArray[i].size(); // ��¼ż��С������
            }
            i++; // ����������
        }
        /*����˼��*/
        i=0;
        for (; pow(2, i) < evenGroupNum || pow(2, i) == evenGroupNum; i++)
        {
            if (pow(2, i) > evenGroupNum)
                break;
        }
        int gap=evenGroupNum-pow(2,i-1);//�������Ϊż����С��������������С������ӽ���2��n���ݵĲ�ֵ
        if(gap!=0)//��ֵ��Ϊ�㣬˵������Ϊż����С���������ʽ�ֽ���������
        //ż��С��������������С������������������=��ֵ*ż��С����*2+(��ֵ-1)*����С����*2,��С�ڵ�����=��ֵ*ż��С����*2+(��ֵ+1)*����С����*2
        roundOneNumber = (oddGroupNum < evenGroupNum) ? gap*2*evenGroup + (gap-1)*2*oddGroup : gap*2*evenGroup +(gap+1)*2*oddGroup;
        /*��ֵΪ�㣬˵������Ϊż����С���������2��n�η���ż��С��������������С������������������=2*����С������*����С��������
          ����С������ӽ���2��n���ݵĲ�ֵ������Ϊ����С����*2 */
        else roundOneNumber = (oddGroupNum < evenGroupNum) ? 2*oddGroup*(oddGroupNum-pow(2,i-2)):oddGroup*2;
        byeRoundNumber = number - roundOneNumber;                         // �������������������������ֿ�����
        byeRoundArray = Select(tempNameArray, byeRoundNumber);            // �����е���Ա�����ѡ�� byeRoundNumber ������Ϊ�ֿ���Ա������һ����Ϊ byeRoundArray �Ķ�ά����
        roundOneArray = deleteSameElements(tempNameArray, byeRoundArray); // �����е���Ա��ȥ���ֿ���Ա������һ����Ϊ roundOneArray �Ķ�ά����
        groupArray = roundOneArray;                                       // �� roundOneArray ���Ƶ� groupArray���������Ա��� roundOneArray ���޸�ʱӰ�쵽 groupArray
        /*��ÿ���ֿ�С���е���Ա���뵽��һ��С���У�����һ���µ���Ϊ groupArray �Ķ�ά������
        ����ÿ��һά������ʾһ������С�飬������Ҫ�����������Ա���ֿյ���Ա��*/
        for (int i = 0; i < groupArray.size() && i < byeRoundArray.size(); i++)
            groupArray[i].insert(groupArray[i].end(), byeRoundArray[i].begin(), byeRoundArray[i].end());
        printList(out_file, "\n��һ���ֿ��������£�", byeRoundArray); // ��ӡ��һ���ֿ�����
        printList(out_file, "\n��һ�ֶ����������£�", roundOneArray); // ��ӡ��һ�ֶ�������
        printList(out_file, "\n�ܷ��������£�", groupArray);        // ��ӡ�ܷ�����
    }
    out_file.close();
}

// ������Ϊ printList �ĺ���������ֵΪ�գ����ڴ�ӡ������������ļ���
void Draw::printList(ofstream &out_file, string note, vector<vector<int>> &Array)
{
    vector<vector<string>> List;           // ����һ����ά�ַ������� List
    for (int i = 0; i < Array.size(); i++) // ������������ Array ��Ԫ��
    {
        vector<string> row;                       // ����һ���ַ������� row
        for (int j = 0; j < Array[i].size(); j++) // ������������ Array[i] ��Ԫ��
        {
            row.push_back(name[Array[i][j]]); // �� row ����ĩβ��� name[Array[i][j]]
        }
        List.push_back(row); // �� row ������ӵ� List ����ĩβ
    }
    for (int i = 0; i <= 90; i++) // ��� 90 ���»���
        cout << "_";
    cout << note << endl;     // ��� note ������
    out_file << note << endl; // ������ļ���д�� note ������
    int i = 0;                // ��ʼ�� i Ϊ 0
    for (auto vec : List)     // ������ά�ַ������� List ��ÿһ������
    {
        cout << "�� " << i + 1 << " ��"                  // ������
             << "(" << countNonEmpty(List[i]) << ")"     // �����ǰ��ķǿ�Ԫ������
             << ":";                                     // ���ð��
        out_file << "�� " << i + 1 << " ��"              // ������ļ���д�����
                 << "(" << countNonEmpty(List[i]) << ")" // ������ļ���д�뵱ǰ��ķǿ�Ԫ������
                 << ":";                                 // ������ļ���д��ð��
        for (auto str : vec)                             // ������ǰ�����е�ÿһ���ַ���
        {
            out_file << str << " "; // ������ļ���д�뵱ǰ�ַ���
            cout << str << " ";     // �����ǰ�ַ�������ĩβ���һ���ո�
        }
        out_file << endl; // ������ļ��л���
        cout << endl;     // ���һ������
        i++;              // i ���� 1
    }
    i = 0;                   // �� i ����Ϊ 0
    if (Array == groupArray) // ������������һ�ֺ��������ͬ��������ѡ�ֶ������˱������Է��������Э�߻�������Excel�����ĸ�ʽ���������
    {
        cin.get(); // ���ջس�
        cout << "������������ʺϱ���Excel��������ʽ���" << endl;
        cin.get();
        for (auto vec : List) // ����������
        {
            cout << "\n�� " << i + 1 << " ��"
                 << "(" << countNonEmpty(List[i]) << ")\n"; // ���������ź�ÿ������

            out_file << "\n�� " << i + 1 << " ��"
                     << "(" << countNonEmpty(List[i]) << ")\n";

            for (auto str : vec) // ����ÿ���ѡ������
            {
                out_file << str << endl
                         << endl; // ���ÿ��ѡ���������ļ���
                cout << str << endl
                     << endl; // ���ÿ��ѡ������������̨��
            }
            out_file << endl;
            cout << endl;
            i++;
        }
    }
    cout << "�����ڣ�" << getTime() << endl;
    out_file << "�����ڣ�" << getTime() << endl; // �������ʱ�䵽�ļ��Ϳ���̨
}

int main()
{
    Draw dr; // ���� Draw ����� dr������ִ�г�ǩ������
    int gameOption = 0, eventOption = 1;
    cout << "���������ʱ�������κδ�����������������д���������رղ���������" << endl;
    cout << "�������Ӧ����ѡ����Ŀ: 1 ������(��̭��) 2 ������(ѭ����) 3 ������(��̭��) 4 ������(ѭ����) ��������� ����\n"; // �����ǩ��Ŀѡ��
    cin >> gameOption;                                                                                                       // �ȴ��û�����ѡ��
    if (gameOption == singleGame || gameOption == singleGameLoop)                                                            // ����û�ѡ��������̭��������ѭ����
    {
        cout << "�������Ӧ����ѡ����Ŀ: 1 ���� 2˫�� ��������� ����\n";
        cin >> eventOption;
        if (eventOption == 1)
            cout << "�����뵥������(����������ʱΪ��������)��"; // ��ʾ�û�������������������ѡ������
        else if (eventOption == 2)
            cout << "������˫�������(����������ʱΪ��������)��";
        else
            return 0;
    }
    else if (gameOption == teamGameLoop || gameOption == teamGame) // ����û�ѡ����������̭����������ѭ����
        cout << "�����������(����������ʱΪ��������)��";          // Ҫ���û����������
    else
        return 0;
    cin >> dr.number;                              // ������������������ѡ������
    cin.get();                                     // ���ջس�
    dr.name.resize(dr.number);                     // Ϊ dr.name ���������ڴ�
    cout << "\n����������������������������0����"; // ��ʾ�û�����������
    cin >> dr.seededNumber;                        // ����������
    cin.get();                                     // ���ջس�
    dr.seededName.resize(dr.seededNumber);         // Ϊ dr.seededName ���������ڴ�
    if (eventOption != 2)
    {
        cout << "�� ���� ����������" << endl; // ��ʾ�û�����ÿ���˵�����
        for (int i = 0; i < dr.number; i++)   // ���ζ���ÿ���˵�����
            getline(cin, dr.name[i]);
        if (dr.seededNumber != 0) // ���������ѡ��
        {
            cout << "�� ���� ��������������" << endl; // ��ʾ�û�����ÿ������ѡ�ֵ�����
            for (int i = 0; i < dr.seededNumber; i++) // ���ζ���ÿ������ѡ�ֵ�����
                getline(cin, dr.seededName[i]);
        }
    }
    if (eventOption == 2)
    {
        vector<string> temp;
        temp.resize(dr.number);
        cout << "�� ���� ����˫���һ��ѡ��������" << endl; // ��ʾ�û�����ÿ���˵�����
        for (int i = 0; i < dr.number; i++)                 // ���ζ���ÿ���˵�����
            getline(cin, dr.name[i]);
        cout << "�� ���� ����˫���һ��ѡ�ֵĶ���������" << endl; // ��ʾ�û�����ÿ���˵�����
        for (int i = 0; i < dr.number; i++)                       // ���ζ���ÿ���˵�����
        {
            getline(cin, temp[i]);
            dr.name[i] = "[" + dr.name[i] + " " + temp[i] + "]";
        }
        if (dr.seededNumber != 0) // ���������ѡ��
        {
            temp.clear();
            temp.resize(dr.seededNumber);
            cout << "�� ���� ����˫�����ӵ�һ��ѡ��������" << endl; // ��ʾ�û�����ÿ������ѡ�ֵ�����
            for (int i = 0; i < dr.seededNumber; i++) // ���ζ���ÿ������ѡ�ֵ�����
                getline(cin, temp[i]);
            cout << "�� ���� ����˫�����ӵ�һ��ѡ�ֵĶ���������" << endl; // ��ʾ�û�����ÿ������ѡ�ֵ�����
            for (int i = 0; i < dr.seededNumber; i++) // ���ζ���ÿ������ѡ�ֵ�����
            {    
                getline(cin, dr.seededName[i]);
                dr.seededName[i]="[" + dr.seededName[i] + " " + temp[i] + "]";
            }
        }
    }
    cout << "������С��ĸ�����";
    cin >> dr.groupNumber;     // Ҫ���û�����С��ĸ�����������洢�� dr.groupNumber ������
    dr.generation(gameOption); // ���� dr.generation(option) ���������ɱ������������г�ǩ����
    system("pause");           // ������ system("pause") ������ʹ������ͣ���У�ֱ���û��������������ִ��
}
