package io.zershyan.examplemod.registry.attachment;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import io.zershyan.forgeattachment.attachment.AttachmentType;
import io.zershyan.forgeattachment.network.RegistryFriendlyByteBuf;
import io.zershyan.forgeattachment.network.codec.StreamCodec;
import net.minecraft.network.FriendlyByteBuf;

/** 玩家状态附件数据：持久化 + 死亡复制 + 同步 */
public class ExampleStatusData {
    public static final Codec<ExampleStatusData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            Codec.INT.fieldOf("value").forGetter(ExampleStatusData::getValue)
    ).apply(instance, ExampleStatusData::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, ExampleStatusData> STREAM_CODEC = StreamCodec.composite(
            StreamCodec.of(FriendlyByteBuf::writeVarInt, FriendlyByteBuf::readVarInt),
            ExampleStatusData::getValue,
            ExampleStatusData::new
    );

    private int value;

    public ExampleStatusData() {
        this(0);
    }

    public ExampleStatusData(int value) {
        this.value = value;
    }

    public int getValue() {
        return value;
    }

    public void setValue(int value) {
        this.value = value;
    }

    public static AttachmentType<ExampleStatusData> createType() {
        return AttachmentType.builder(() -> new ExampleStatusData(0))
                .serialize(CODEC)
                .copyOnDeath()
                .sync(STREAM_CODEC)
                .build();
    }
}
