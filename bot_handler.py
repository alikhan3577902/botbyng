import asyncio
import logging
import re
from typing import Dict, Any
from pyrogram.types import Message

logger = logging.getLogger(__name__)

class BotHandler:
    def __init__(self, telegram_client, bot_username: str):
        self.telegram_client = telegram_client
        self.bot_username = bot_username
        self.response_timeout = 15  # seconds

    async def _send_start_command(self):
        """Send /start command to the bot"""
        try:
            await self.telegram_client.send_message(self.bot_username, "/start")
            await asyncio.sleep(1)  # Reduced wait time
            logger.info("Sent /start command to bot")
        except Exception as e:
            logger.error(f"Failed to send /start command: {e}")
            raise

    async def _get_latest_bot_message(self) -> Message:
        """Get the latest message from the bot"""
        try:
            messages = await self.telegram_client.get_messages(self.bot_username, limit=3)
            if messages:
                # Look for message with inline keyboard
                for message in messages:
                    if message.reply_markup and message.reply_markup.inline_keyboard:
                        # Handle potential encoding issues
                        try:
                            text_preview = message.text[:100] if message.text else 'No text'
                            logger.info(f"Found message with inline keyboard: {text_preview}")
                        except UnicodeDecodeError:
                            logger.info("Found message with inline keyboard (encoding issue with text)")
                        return message
                # If no keyboard found, return the latest message
                logger.warning("No message with inline keyboard found, returning latest message")
                return messages[0]
            else:
                raise Exception("No messages found from bot")
        except Exception as e:
            logger.error(f"Failed to get latest bot message: {e}")
            raise

    async def _click_button_and_wait(self, button_text: str, input_value: str) -> str:
        """Click a button and send input, then wait for response"""
        try:
            # Send /start to refresh the menu
            await self._send_start_command()

            # Get the menu message with inline buttons
            menu_message = await self._get_latest_bot_message()

            # Debug: Log the message content and available buttons
            try:
                text_preview = menu_message.text[:200] if menu_message.text else 'No text'
                logger.info(f"Menu message text: {text_preview}")
            except UnicodeDecodeError:
                logger.info("Menu message text has encoding issues")

            if menu_message.reply_markup and menu_message.reply_markup.inline_keyboard:
                available_buttons = []
                for row in menu_message.reply_markup.inline_keyboard:
                    for button in row:
                        try:
                            available_buttons.append(button.text)
                        except UnicodeDecodeError:
                            available_buttons.append("[encoding error]")
                logger.info(f"Available buttons: {available_buttons}")
                logger.info(f"Looking for button: {button_text}")
            else:
                logger.error("No inline keyboard found in menu message")
                raise Exception("Bot menu has no inline keyboard")

            # Click the specified button
            await self.telegram_client.click_inline_button(menu_message, button_text)
            await asyncio.sleep(1.5)

            # Send the input value
            await self.telegram_client.send_message(self.bot_username, input_value)

            # Wait for the bot to process and send all results
            await asyncio.sleep(4)

            # Get messages to capture bot responses
            response_messages = await self.telegram_client.get_messages(self.bot_username, limit=5)

            # Look specifically for the search results messages
            result_messages = []

            for message in response_messages:
                try:
                    if message.text and message.text != input_value:
                        text = message.text

                        # Look for the actual search results (not menu or format messages)
                        # For FamPay, specifically look for the main data message
                        if (("Number Info Results:" in text) or 
                            ("Result 1:" in text) or 
                            ("Showing" in text and "Result" in text) or
                            ("FamPay Information" in text) or
                            ("𝗙𝗮𝗺𝗣𝗮𝘆 𝗜𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻" in text) or
                            ("🎯" in text and "𝗙𝗮𝗺𝗣𝗮𝘆" in text) or
                            ("𝗡𝗮𝗺𝗲:" in text and "𝗨𝗣𝗜 𝗜𝗗:" in text) or
                            ("Name:" in text and "UPI ID:" in text)):

                            # Skip the menu messages but include the main data message
                            if ("Select a service from the menu below:" not in text and
                                "𝐒𝐞𝐥𝐞𝐜𝐭 𝐚 𝐬𝐞𝐫𝐯𝐢𝐜𝐞" not in text):
                                logger.info(f"Found search result message: {text[:100]}...")
                                result_messages.append(text)
                                break  # Take only the first main result message

                except UnicodeDecodeError:
                    logger.warning("Message has encoding issues, trying to handle...")
                    try:
                        if hasattr(message, 'text') and message.text:
                            text = message.text.encode('utf-8', errors='ignore').decode('utf-8')
                            if (text != input_value and 
                                (("Number Info Results:" in text) or 
                                 ("Result 1:" in text) or 
                                 ("Showing" in text and "Result" in text) or
                                 ("Credits Used:" in text) or
                                 ("𝗙𝗮𝗺𝗣𝗮𝘆" in text))):
                                result_messages.append(text)
                    except:
                        continue

            # If we found search result messages, combine them
            if result_messages:
                # Combine all the search result messages
                full_response = "\n\n".join(result_messages)
                logger.info(f"Returning search results with {len(result_messages)} messages")
                return full_response

            # If no search results found, look for any response that's not the menu
            for message in response_messages:
                try:
                    if (message.text and 
                        message.text != input_value and 
                        "/start" not in message.text and
                        "Select a service from the menu below:" not in message.text and
                        "Please send the phone number" not in message.text):
                        logger.info(f"Fallback: returning message: {message.text[:100]}...")
                        return message.text
                except:
                    continue

            return "No valid search results received from bot"

        except Exception as e:
            logger.error(f"Failed to interact with bot: {e}")
            raise

    def _parse_response_to_json(self, response_text: str, query_type: str) -> Dict[str, Any]:
        """Return original bot response with emojis and formatting"""
        try:
            result = {
                "status": "success",
                "service": "MY EYE OSINT BOT",
                "query_type": query_type,
                "data": {
                    "original_response": response_text
                }
            }

            return result

        except Exception as e:
            logger.error(f"Failed to handle response: {e}")
            return {
                "status": "error", 
                "error_message": f"Failed to handle response: {str(e)}",
                "raw_response": response_text if response_text else "No response"
            }

    def _clean_and_parse_response(self, text: str, query_type: str) -> Dict[str, Any]:
        """Clean emojis and parse structured data from bot response"""
        import re

        # Remove emojis and special characters
        emoji_pattern = re.compile("["
                                  u"\U0001F600-\U0001F64F"  # emoticons
                                  u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                  u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                  u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                  u"\U00002702-\U000027B0"
                                  u"\U000024C2-\U0001F251"
                                  u"\U0001F900-\U0001F9FF"  # supplemental symbols
                                  "]+", flags=re.UNICODE)

        cleaned_text = emoji_pattern.sub('', text)

        # Remove decorative elements
        cleaned_text = re.sub(r'━+', '', cleaned_text)
        cleaned_text = re.sub(r'⚫+', '', cleaned_text)

        data = {}

        # Parse based on query type
        if query_type == "fampay":
            data = self._parse_fampay_response(cleaned_text)
        elif query_type == "number_info":
            data = self._parse_number_response(cleaned_text)
        elif query_type == "aadhar":
            data = self._parse_aadhar_response(cleaned_text)
        elif query_type == "vehicle":
            data = self._parse_vehicle_response(cleaned_text)
        elif query_type == "ration":
            data = self._parse_ration_response(cleaned_text)
        elif query_type == "breach":
            data = self._parse_breach_response(cleaned_text)
        elif query_type == "challan":
            data = self._parse_challan_response(cleaned_text)
        elif query_type == "upi":
            data = self._parse_upi_response(cleaned_text)
        else:
            data = {"raw_data": cleaned_text}

        # Extract credits info if present
        credits_match = re.search(r'Credits Used:\s*(\d+)\s*\|\s*Remaining:\s*([\d.]+)', text)
        if credits_match:
            data["credits_used"] = int(credits_match.group(1))
            data["credits_remaining"] = float(credits_match.group(2))

        return data

    def _parse_fampay_response(self, text: str) -> Dict[str, Any]:
        """Parse FamPay specific response"""
        data = {}
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle FamPay specific fields - look for the stylized text patterns
            if '𝗡𝗮𝗺𝗲:' in line:
                data['name'] = line.split('𝗡𝗮𝗺𝗲:', 1)[1].strip()
            elif '𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲:' in line:
                data['username'] = line.split('𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲:', 1)[1].strip()
            elif '𝗗𝗶𝘀𝗽𝗹𝗮𝘆 𝗡𝗮𝗺𝗲:' in line:
                data['display_name'] = line.split('𝗗𝗶𝘀𝗽𝗹𝗮𝘆 𝗡𝗮𝗺𝗲:', 1)[1].strip()
            elif '𝗨𝗣𝗜 𝗜𝗗:' in line:
                data['upi_id'] = line.split('𝗨𝗣𝗜 𝗜𝗗:', 1)[1].strip()
            elif '𝗠𝗼𝗯𝗶𝗹𝗲:' in line:
                data['mobile'] = line.split('𝗠𝗼𝗯𝗶𝗹𝗲:', 1)[1].strip()
            elif '𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗧𝘆𝗽𝗲:' in line:
                data['account_type'] = line.split('𝗔𝗰𝗰𝗼𝘂𝗻𝘁 𝗧𝘆𝗽𝗲:', 1)[1].strip()
            elif '𝗕𝗲𝗻𝗲𝗳𝗶𝗰𝗶𝗮𝗿𝘆 𝗦𝘁𝗮𝘁𝘂𝘀:' in line:
                data['beneficiary_status'] = line.split('𝗕𝗲𝗻𝗲𝗳𝗶𝗰𝗶𝗮𝗿𝘆 𝗦𝘁𝗮𝘁𝘂𝘀:', 1)[1].strip()
            elif '𝗨𝘀𝗲𝗿 𝗦𝘁𝗮𝘁𝘂𝘀:' in line:
                data['user_status'] = line.split('𝗨𝘀𝗲𝗿 𝗦𝘁𝗮𝘁𝘂𝘀:', 1)[1].strip()
            # Also handle regular text versions as fallback
            elif 'Name:' in line:
                data['name'] = line.split('Name:', 1)[1].strip()
            elif 'Username:' in line:
                data['username'] = line.split('Username:', 1)[1].strip()
            elif 'Display Name:' in line:
                data['display_name'] = line.split('Display Name:', 1)[1].strip()
            elif 'UPI ID:' in line:
                data['upi_id'] = line.split('UPI ID:', 1)[1].strip()
            elif 'Mobile:' in line:
                data['mobile'] = line.split('Mobile:', 1)[1].strip()
            elif 'Account Type:' in line:
                data['account_type'] = line.split('Account Type:', 1)[1].strip()
            elif 'Beneficiary Status:' in line:
                data['beneficiary_status'] = line.split('Beneficiary Status:', 1)[1].strip()
            elif 'User Status:' in line:
                data['user_status'] = line.split('User Status:', 1)[1].strip()

        return data

    def _parse_number_response(self, text: str) -> Dict[str, Any]:
        """Parse number info response"""
        data = {}
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if ':' in line and line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(' ', '_')
                    value = parts[1].strip()
                    data[key] = value

        return data

    def _parse_aadhar_response(self, text: str) -> Dict[str, Any]:
        """Parse Aadhar info response"""
        return self._parse_generic_response(text)

    def _parse_vehicle_response(self, text: str) -> Dict[str, Any]:
        """Parse vehicle info response"""
        return self._parse_generic_response(text)

    def _parse_ration_response(self, text: str) -> Dict[str, Any]:
        """Parse ration info response"""
        return self._parse_generic_response(text)

    def _parse_breach_response(self, text: str) -> Dict[str, Any]:
        """Parse breach info response"""
        return self._parse_generic_response(text)

    def _parse_challan_response(self, text: str) -> Dict[str, Any]:
        """Parse challan info response"""
        return self._parse_generic_response(text)

    def _parse_upi_response(self, text: str) -> Dict[str, Any]:
        """Parse UPI info response"""
        return self._parse_generic_response(text)

    def _parse_generic_response(self, text: str) -> Dict[str, Any]:
        """Generic parser for responses"""
        data = {}
        lines = text.split('\n')

        for line in lines:
            line = line.strip()
            if ':' in line and line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower().replace(' ', '_')
                    value = parts[1].strip()
                    data[key] = value

        return data



    # Public API methods
    async def get_number_info(self, number: str) -> Dict[str, Any]:
        """Get information about a phone number"""
        response = await self._click_button_and_wait("📱 𝗡𝘂𝗺𝗯𝗲𝗿 𝗜𝗻𝗳𝗼", number)
        return self._parse_response_to_json(response, "number_info")

    async def get_fampay_info(self, fam_id: str) -> Dict[str, Any]:
        """Get FamPay information"""
        response = await self._click_button_and_wait("💳 𝗙𝗔𝗠𝗣𝗔𝗬 𝗜𝗡𝗙𝗢", fam_id)
        return self._parse_response_to_json(response, "fampay")

    async def get_aadhar_info(self, aadhar_id: str) -> Dict[str, Any]:
        """Get Aadhar information"""
        response = await self._click_button_and_wait("🆔 𝗔𝗮𝗱𝗵𝗮𝗿 𝗜𝗻𝗳𝗼", aadhar_id)
        return self._parse_response_to_json(response, "aadhar")

    async def get_vehicle_info(self, vehicle_id: str) -> Dict[str, Any]:
        """Get vehicle information"""
        response = await self._click_button_and_wait("🚗 𝗩𝗲𝗵𝗶𝗰𝗹𝗲 𝗜𝗻𝗳𝗼", vehicle_id)
        return self._parse_response_to_json(response, "vehicle")

    async def get_ration_info(self, ration_id: str) -> Dict[str, Any]:
        """Get ration card information"""
        response = await self._click_button_and_wait("📋 𝗥𝗔𝗧𝗜𝗢𝗡 𝗦𝗘𝗔𝗥𝗖𝗛", ration_id)
        return self._parse_response_to_json(response, "ration")

    async def get_breach_info(self, email: str) -> Dict[str, Any]:
        """Get breach information"""
        response = await self._click_button_and_wait("🔍 𝗕𝗥𝗘𝗔𝗖𝗛 𝗜𝗡𝗙𝗢", email)
        return self._parse_response_to_json(response, "breach")

    async def get_challan_info(self, vehicle_number: str) -> Dict[str, Any]:
        """Get challan information"""
        response = await self._click_button_and_wait("🚨 𝗖𝗛𝗔𝗟𝗟𝗔𝗡 𝗜𝗡𝗙𝗢", vehicle_number)
        return self._parse_response_to_json(response, "challan")

    async def get_upi_info(self, upi_id: str) -> Dict[str, Any]:
        """Get UPI information"""
        response = await self._click_button_and_wait("💰 𝗨𝗣𝗜 𝗜𝗡𝗙𝗢", upi_id)
        return self._parse_response_to_json(response, "upi")