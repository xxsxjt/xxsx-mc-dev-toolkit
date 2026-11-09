package io.zershyan.examplemod.util.mixin.examplemod.common;

/** 由 MixinLivingEntity 实现，把注入的成员暴露给普通代码 */
public interface IMixinLivingEntity {

    /** 示例：暴露一个由 mixin 注入的标记位 */
    boolean examplemod$isMarked();

    void examplemod$setMarked(boolean marked);
}