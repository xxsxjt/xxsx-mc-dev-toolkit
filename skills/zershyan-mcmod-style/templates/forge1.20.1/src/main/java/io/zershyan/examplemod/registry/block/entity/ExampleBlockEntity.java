package io.zershyan.examplemod.registry.block.entity;

import io.zershyan.examplemod.registry.ExampleModBlockEntityTypes;
import net.minecraft.core.BlockPos;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public class ExampleBlockEntity extends BlockEntity {
    private int value;

    public ExampleBlockEntity(BlockPos pos, BlockState state) {
        super(ExampleModBlockEntityTypes.EXAMPLE_BLOCK_ENTITY.get(), pos, state);
    }

    public int getValue() {
        return value;
    }

    public void setValue(int value) {
        this.value = value;
        setChanged();
    }

    @Override
    protected void saveAdditional(CompoundTag tag) {
        super.saveAdditional(tag);
        tag.putInt("value", value);
    }

    @Override
    public void load(CompoundTag tag) {
        super.load(tag);
        value = tag.getInt("value");
    }
}
