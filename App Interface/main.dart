import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';

void main() {
  runApp(const EmergencyChatbot());
}

class EmergencyChatbot extends StatelessWidget {
  const EmergencyChatbot({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Emergency Chatbot',
      theme: ThemeData(primarySwatch: Colors.red),
      home: const ChatScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Map<String, dynamic>> _messages = [];
  int _step = -1; // -1 for language selection, 0 to 4 for steps
  String _selectedLanguage = "";

  String location = "";
  Set<String> selectedServices = {};
  String intensity = "";
  String persons = "";

  final Map<String, Map<String, String>> translations = {
    'en': {
      'language_prompt': 'Which language are you comfortable in?',
      'yes': 'Yes',
      'no': 'No',
      'hello': 'Hello! Are you in an emergency?',
      'fetching_location': '📍 Fetching your location...',
      'your_location': 'Your location: ',
      'which_service': 'Which service do you need?',
      'selected': 'Selected: ',
      'intensity': 'What is the intensity of the accident?',
      'how_many': 'How many people are involved?',
      'thank_you': '✅ Thanks for reporting. Help is on the way!',
      'disabled': '❌ Location services disabled.',
      'permission_denied': '❌ Location permission denied.',
      'permission_denied_permanent': '❌ Location permission permanently denied.',
      'failed_location': '❌ Failed to get location.',
      'stay_safe': 'Stay safe! You can reach out if needed.',
      'confirm_selection': 'Confirm Selection',
      'number_people': 'Number of people'
    },
    'ta': {
      'language_prompt': 'நீங்கள் எந்த மொழியில் வசதியாக இருக்கிறீர்கள்?',
      'yes': 'ஆம்',
      'no': 'இல்லை',
      'hello': 'வணக்கம்! நீங்கள் அவசர நிலையில் உள்ளீர்களா?',
      'fetching_location': '📍 உங்கள் இருப்பிடத்தை பெறுகிறது...',
      'your_location': 'உங்கள் இருப்பிடம்: ',
      'which_service': 'உங்களுக்கு எந்த சேவை தேவை?',
      'selected': 'தேர்ந்தெடுக்கப்பட்டது: ',
      'intensity': 'விபத்து தீவிரம் என்ன?',
      'how_many': 'எத்தனை பேர்?',
      'thank_you': '✅ தகவல் வழங்கியதற்காக நன்றி. உதவி வரும் வழியில் உள்ளது!',
      'disabled': '❌ இருப்பிட சேவைகள் முடக்கப்பட்டுள்ளன.',
      'permission_denied': '❌ இருப்பிட அனுமதி மறுக்கப்பட்டது.',
      'permission_denied_permanent': '❌ இருப்பிட அனுமதி நிரந்தரமாக மறுக்கப்பட்டது.',
      'failed_location': '❌ இருப்பிடத்தை பெற முடியவில்லை.',
      'stay_safe': 'பாதுகாப்பாக இருங்கள்! தேவையெனில் எங்களை அணுகலாம்.',
      'confirm_selection': 'தேர்வை உறுதி செய்க',
      'number_people': 'மக்களின் எண்ணிக்கை'
    },
    'hi': {
      'language_prompt': 'आप किस भाषा में सहज हैं?',
      'yes': 'हाँ',
      'no': 'नहीं',
      'hello': 'नमस्ते! क्या आप आपातकाल में हैं?',
      'fetching_location': '📍 आपका स्थान प्राप्त किया जा रहा है...',
      'your_location': 'आपका स्थान: ',
      'which_service': 'आपको कौन सी सेवा चाहिए?',
      'selected': 'चयनित: ',
      'intensity': 'दुर्घटना की तीव्रता क्या है?',
      'how_many': 'कितने लोग शामिल हैं?',
      'thank_you': '✅ सूचना के लिए धन्यवाद। सहायता रास्ते में है!',
      'disabled': '❌ स्थान सेवाएँ अक्षम हैं।',
      'permission_denied': '❌ स्थान अनुमति अस्वीकृत।',
      'permission_denied_permanent': '❌ स्थान अनुमति स्थायी रूप से अस्वीकृत।',
      'failed_location': '❌ स्थान प्राप्त करने में विफल।',
      'stay_safe': 'सुरक्षित रहें! आवश्यकता हो तो संपर्क करें।',
      'confirm_selection': 'चयन की पुष्टि करें',
      'number_people': 'लोगों की संख्या'
    },
  };

  @override
  void initState() {
    super.initState();
    _step = -1;
    _addBotMessage("${translations['en']!['language_prompt']}");
  }

  void _setLanguage(String langCode) {
    setState(() {
      _selectedLanguage = langCode;
      _messages.clear();
      _step = 0;
      _addBotMessage(translations[_selectedLanguage]!['hello']!);
    });
  }

  void _addBotMessage(String text) {
    setState(() {
      _messages.add({"role": "bot", "text": text});
    });
  }

  void _addUserMessage(String text) {
    setState(() {
      _messages.add({"role": "user", "text": text});
    });
  }

  void _handleYesNo(String choice) async {
    _addUserMessage(choice);
    if (choice == translations[_selectedLanguage]!['yes']) {
      _addBotMessage(translations[_selectedLanguage]!['fetching_location']!);
      location = await _getLocation();
      _addBotMessage("${translations[_selectedLanguage]!['your_location']}$location");

      _addBotMessage(translations[_selectedLanguage]!['which_service']!);
      _step = 1;
    } else {
      _addBotMessage(translations[_selectedLanguage]!['stay_safe']!);
      _step = -1;
    }
  }

  void _handleServiceSelect(String service) {
    setState(() {
      if (selectedServices.contains(service)) {
        selectedServices.remove(service);
      } else {
        selectedServices.add(service);
      }
    });
  }

  void _confirmServices() {
    _addUserMessage("${translations[_selectedLanguage]!['selected']}${selectedServices.join(', ')}");
    _addBotMessage(translations[_selectedLanguage]!['intensity']!);
    _step = 2;
  }

  void _handleIntensity(String level) {
    intensity = level;
    _addUserMessage(level);
    _addBotMessage(translations[_selectedLanguage]!['how_many']!);
    _step = 3;
  }

  void _handlePersonsEntered(String count) {
    persons = count;
    _addUserMessage("$count person(s)");
    _addBotMessage(translations[_selectedLanguage]!['thank_you']!);
    _step = 4;
  }

  Future<String> _getLocation() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return translations[_selectedLanguage]!['disabled']!;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        return translations[_selectedLanguage]!['permission_denied']!;
      }
    }
    if (permission == LocationPermission.deniedForever) {
      return translations[_selectedLanguage]!['permission_denied_permanent']!;
    }

    try {
      Position pos = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      return "${pos.latitude}, ${pos.longitude}";
    } catch (e) {
      return translations[_selectedLanguage]!['failed_location']!;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Emergency Chatbot")),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(10),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                bool isUser = msg["role"] == "user";
                return Align(
                  alignment:
                      isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: isUser ? Colors.blue[100] : Colors.grey[300],
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(msg["text"]),
                  ),
                );
              },
            ),
          ),
          if (_step == -1) ...[
            _buildLanguageSelection()
          ] else if (_step == 0) ...[
            _buildYesNoOptions()
          ] else if (_step == 1) ...[
            _buildServiceOptions()
          ] else if (_step == 2) ...[
            _buildIntensityOptions()
          ] else if (_step == 3) ...[
            _buildPersonInput()
          ],
        ],
      ),
    );
  }

  Widget _buildLanguageSelection() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _buildOptionButton("English", () => _setLanguage("en")),
        const SizedBox(width: 10),
        _buildOptionButton("தமிழ்", () => _setLanguage("ta")),
        const SizedBox(width: 10),
        _buildOptionButton("हिंदी", () => _setLanguage("hi")),
      ],
    );
  }

  Widget _buildYesNoOptions() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _buildOptionButton(translations[_selectedLanguage]!['yes']!, () => _handleYesNo(translations[_selectedLanguage]!['yes']!)),
        const SizedBox(width: 10),
        _buildOptionButton(translations[_selectedLanguage]!['no']!, () => _handleYesNo(translations[_selectedLanguage]!['no']!)),
      ],
    );
  }

  Widget _buildServiceOptions() {
    return Column(
      children: [
        Wrap(
          spacing: 10,
          children: ["Ambulance", "Police", "Firemen"].map((service) {
            final isSelected = selectedServices.contains(service);
            return ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: isSelected ? Colors.green : null,
              ),
              onPressed: () => _handleServiceSelect(service),
              child: Text(service),
            );
          }).toList(),
        ),
        TextButton(
          onPressed: _confirmServices,
          child: Text(translations[_selectedLanguage]!['confirm_selection']!),
        )
      ],
    );
  }

  Widget _buildIntensityOptions() {
    return Wrap(
      spacing: 10,
      children: ["High", "Danger", "Medium"].map((level) {
        return ElevatedButton(
          onPressed: () => _handleIntensity(level),
          child: Text(level),
        );
      }).toList(),
    );
  }

  Widget _buildPersonInput() {
    final TextEditingController _personController = TextEditingController();
    return Padding(
      padding: const EdgeInsets.all(8),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _personController,
              keyboardType: TextInputType.number,
              decoration: InputDecoration(
                labelText: translations[_selectedLanguage]!['number_people'],
                border: const OutlineInputBorder(),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.send),
            onPressed: () => _handlePersonsEntered(_personController.text.trim()),
          )
        ],
      ),
    );
  }

  Widget _buildOptionButton(String label, VoidCallback onPressed) {
    return ElevatedButton(
      onPressed: onPressed,
      child: Text(label),
    );
  }
}
