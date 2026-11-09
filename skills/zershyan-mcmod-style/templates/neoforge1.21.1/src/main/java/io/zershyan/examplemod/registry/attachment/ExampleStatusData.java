package io.zershyan.examplemod.registry.attachment;

import com.mojang.serialization.Codec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;

/** 玩家状态附件数据 */
public class ExampleStatusData {
    public static final Codec<ExampleStatusData> CODEC = RecordCodecBuilder.create(instance -> instance.group(
            Codec.INT.fieldOf("value").forGetter(ExampleStatusData::getValue)
    ).apply(instance, ExampleStatusData::new));

    public static final StreamCodec<RegistryFriendlyByteBuf, ExampleStatusData> STREAM_CODEC = StreamCodec.composite(
            ByteBufCodecs.VAR_INT, ExampleStatusData::getValue,
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
}
