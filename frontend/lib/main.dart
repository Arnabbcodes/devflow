import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';

void main() {
  runApp(const DevFlowApp());
}

class DevFlowApp extends StatelessWidget {
  const DevFlowApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DevFlow',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(useMaterial3: true).copyWith(
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        colorScheme: const ColorScheme.dark(
          primary: Colors.blueAccent,
          secondary: Colors.tealAccent,
          surface: Color(0xFF1E293B),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFF0F172A),
          elevation: 0,
        ),
      ),
      home: const DashboardScreen(),
    );
  }
}

// ==========================================
// 1. DASHBOARD SCREEN
// ==========================================
class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('DevFlow', style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ProfileScreen()),
              );
            },
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Uploading demo-project.zip...')),
          );
          Future.delayed(const Duration(seconds: 1), () {
            if (context.mounted) {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const AnalysisScreen(projectName: 'demo-project/'),
                ),
              );
            }
          });
        },
        icon: const Icon(Icons.upload_file),
        label: const Text('Analyze Project'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Recent Analyses', style: TextStyle(fontSize: 18, color: Colors.grey)),
          const SizedBox(height: 16),
          _buildProjectCard('Todo API', '12 issues', '8 resolved', 85, context),
          _buildProjectCard('Student Portal', '7 issues', '5 resolved', 72, context),
          _buildProjectCard('Weather API', '4 issues', '4 resolved', 98, context),
        ],
      ),
    );
  }

  Widget _buildProjectCard(String title, String issues, String resolved, int score, BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Stack(
          alignment: Alignment.center,
          children: [
            CircularProgressIndicator(
              value: score / 100,
              backgroundColor: Colors.grey[800],
              color: score > 80 ? Colors.green : (score > 60 ? Colors.orange : Colors.red),
            ),
            Text(score.toString(), style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
          ],
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Text('$issues • $resolved'),
        trailing: const Icon(Icons.chevron_right),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => AnalysisScreen(projectName: title),
            ),
          );
        },
      ),
    );
  }
}

// ==========================================
// 2. PROJECT ANALYSIS SCREEN
// ==========================================
class AnalysisScreen extends StatelessWidget {
  final String projectName;

  const AnalysisScreen({super.key, required this.projectName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(projectName)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: Colors.redAccent.withValues(alpha: 0.5)),
              ),
              child: Row(
                children: [
                  SizedBox(
                    height: 100,
                    width: 100,
                    child: PieChart(
                      PieChartData(
                        sectionsSpace: 0,
                        centerSpaceRadius: 40,
                        sections: [
                          PieChartSectionData(color: Colors.redAccent, value: 39, title: '', radius: 10),
                          PieChartSectionData(color: Colors.greenAccent, value: 61, title: '', radius: 10),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(width: 24),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('PROJECT HEALTH', style: TextStyle(color: Colors.grey, letterSpacing: 1.2)),
                      Text('61 / 100', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Colors.redAccent)),
                    ],
                  )
                ],
              ),
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _statChip('🐛 Bugs', '5'),
                _statChip('🔐 Security', '2'),
                _statChip('🧪 Tests', '6'),
              ],
            ),
            const SizedBox(height: 24),
            const Text('Critical Issues', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 12),
            Card(
              color: Colors.redAccent.withValues(alpha: 0.1),
              shape: RoundedRectangleBorder(
                side: const BorderSide(color: Colors.redAccent),
                borderRadius: BorderRadius.circular(8),
              ),
              child: ListTile(
                leading: const Icon(Icons.security, color: Colors.redAccent),
                title: const Text('JWT authentication vulnerability', style: TextStyle(fontWeight: FontWeight.bold)),
                subtitle: const Text('auth.py • Line 42\nMissing signature validation'),
                isThreeLine: true,
                trailing: ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.redAccent),
                  onPressed: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(builder: (_) => const IssueDetailScreen()),
                    );
                  },
                  child: const Text('Fix', style: TextStyle(color: Colors.white)),
                ),
              ),
            ),
            Card(
              child: ListTile(
                leading: const Icon(Icons.bug_report, color: Colors.orange),
                title: const Text('Null reference in User Parser'),
                subtitle: const Text('users.py • Line 112'),
                trailing: TextButton(onPressed: () {}, child: const Text('View')),
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _statChip(String label, String count) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(color: Colors.black26, borderRadius: BorderRadius.circular(20)),
      child: Row(
        children: [
          Text(label),
          const SizedBox(width: 8),
          Text(count, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}

// ==========================================
// 3. ISSUE DETAIL & FIX WORKFLOW SCREEN
// ==========================================
class IssueDetailScreen extends StatefulWidget {
  const IssueDetailScreen({super.key});

  @override
  State<IssueDetailScreen> createState() => _IssueDetailScreenState();
}

class _IssueDetailScreenState extends State<IssueDetailScreen> {
  bool _isFixing = false;
  bool _isVerified = false;
  int _currentStep = 0;

  void _startFixWorkflow() async {
    setState(() {
      _isFixing = true;
    });

    for (int i = 0; i < 4; i++) {
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) {
        setState(() => _currentStep = i + 1);
      }
    }

    if (mounted) {
      setState(() {
        _isFixing = false;
        _isVerified = true;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Issue Details')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('JWT authentication vulnerability', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('auth.py • Line 42', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              width: double.infinity,
              decoration: BoxDecoration(color: Colors.black, borderRadius: BorderRadius.circular(8)),
              child: const Text(
                'def verify_token(token):\n    # TODO: add secret key validation\n    payload = jwt.decode(token, options={"verify_signature": False})\n    return payload',
                style: TextStyle(fontFamily: 'monospace', color: Colors.redAccent),
              ),
            ),
            const SizedBox(height: 24),
            if (!_isFixing && !_isVerified)
              SizedBox(
                width: double.infinity,
                height: 50,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.auto_fix_high),
                  label: const Text('Generate AI Fix Plan'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blueAccent,
                    foregroundColor: Colors.white,
                  ),
                  onPressed: _startFixWorkflow,
                ),
              ),
            if (_isFixing || _isVerified) ...[
              const Divider(height: 40),
              const Text('AI FIX PLAN (IBM Bob 2.0 Orchestration)', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blueAccent)),
              const SizedBox(height: 16),
              _buildStepRow('Identify vulnerable code (Security Agent)', 0),
              _buildStepRow('Generate correction (Backend Agent)', 1),
              _buildStepRow('Generate regression test (Test Agent)', 2),
              _buildStepRow('Verify correction', 3),
            ],
            if (_isVerified) ...[
              const Divider(height: 40),
              const Text('VERIFICATION PASSED ✅', style: TextStyle(fontSize: 20, color: Colors.greenAccent, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(child: _buildBeforeAfterCard('BEFORE', '12', '7', '5')),
                  const SizedBox(width: 16),
                  Expanded(child: _buildBeforeAfterCard('AFTER', '18', '18', '0', isAfter: true)),
                ],
              ),
            ]
          ],
        ),
      ),
    );
  }

  Widget _buildStepRow(String text, int stepIndex) {
    bool isDone = _currentStep > stepIndex;
    bool isActive = _currentStep == stepIndex && _isFixing;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          if (isDone)
            const Icon(Icons.check_circle, color: Colors.greenAccent)
          else if (isActive)
            const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(strokeWidth: 2))
          else
            const Icon(Icons.circle_outlined, color: Colors.grey),
          const SizedBox(width: 12),
          Text(
            text,
            style: TextStyle(
              color: isDone ? Colors.white : (isActive ? Colors.blueAccent : Colors.grey),
              fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBeforeAfterCard(String title, String total, String passed, String failed, {bool isAfter = false}) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isAfter ? Colors.green.withValues(alpha: 0.1) : Colors.red.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: isAfter ? Colors.green : Colors.redAccent),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Text('Tests: $total'),
          Text('Passed: $passed', style: TextStyle(color: isAfter ? Colors.greenAccent : Colors.white)),
          Text('Failed: $failed', style: TextStyle(color: isAfter ? Colors.white : Colors.redAccent)),
        ],
      ),
    );
  }
}

// ==========================================
// 4. PROFILE SCREEN
// ==========================================
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Developer Profile')),
      body: ListView(
        padding: const EdgeInsets.all(24),
        children: [
          const CircleAvatar(
            radius: 50,
            backgroundColor: Colors.blueAccent,
            child: Icon(Icons.person_outline, size: 50, color: Colors.white),
          ),
          const SizedBox(height: 16),
          const Center(
            child: Text('Alex Developer', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
          ),
          const Center(
            child: Text('alex@devflow-demo.com', style: TextStyle(color: Colors.grey)),
          ),
          const SizedBox(height: 32),
          const Text('IBM Bob 2.0 Settings', style: TextStyle(color: Colors.blueAccent, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          SwitchListTile(
            title: const Text('Parallel Agent Execution'),
            subtitle: const Text('Run backend, security, and test agents simultaneously'),
            value: true,
            onChanged: (val) {},
            contentPadding: EdgeInsets.zero,
          ),
          SwitchListTile(
            title: const Text('Auto-generate Regression Tests'),
            subtitle: const Text('Always prompt Test Agent when fixing bugs'),
            value: true,
            onChanged: (val) {},
            contentPadding: EdgeInsets.zero,
          ),
          const Divider(height: 48),
          ListTile(
            leading: const Icon(Icons.history),
            title: const Text('Analysis History'),
            trailing: const Icon(Icons.chevron_right),
            contentPadding: EdgeInsets.zero,
            onTap: () => Navigator.pop(context),
          ),
          ListTile(
            leading: const Icon(Icons.api),
            title: const Text('API Keys & Connections'),
            trailing: const Icon(Icons.chevron_right),
            contentPadding: EdgeInsets.zero,
            onTap: () {},
          ),
          const SizedBox(height: 24),
          OutlinedButton(
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.redAccent,
              side: const BorderSide(color: Colors.redAccent),
            ),
            onPressed: () => Navigator.pop(context),
            child: const Text('Sign Out'),
          )
        ],
      ),
    );
  }
}