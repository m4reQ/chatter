import { Message } from "./Message.ts";

export default class MessageGroup {
    messages: Message[] = [];

    static fromMessage(message: Message) {
        const group = new MessageGroup();
        group.pushMessage(message);

        return group;
    }

    get senderID() {
        return this.messages[0].sender_id;
    }

    get senderUsername() {
        return this.messages[0].sender_username;
    }

    get firstSent() {
        return this.messages.at(-1)!.sent_at;
    }

    pushMessage(message: Message) {
        this.messages.push(message);
    }
}