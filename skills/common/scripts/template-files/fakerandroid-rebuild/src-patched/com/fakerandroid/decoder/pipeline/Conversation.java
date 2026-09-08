package com.fakerandroid.decoder.pipeline;

/* JADX INFO: loaded from: Conversation.class */
public abstract class Conversation {
    public Context context;

    public abstract void converse();

    public Conversation(Context context) {
        this.context = context;
    }
}
